import datetime
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_provider
from app.ai.interface import AIProviderInterface
from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.core.logging import get_logger
from app.models.cover_letter import CoverLetter
from app.models.cv_version import CVVersion
from app.models.job_target import JobTarget
from app.models.profile import CandidateProfile
from app.repositories.interfaces.cover_letter_repository import ICoverLetterRepository
from app.repositories.interfaces.cv_version_repository import ICVVersionRepository
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.cover_letter_repository import PostgresCoverLetterRepository
from app.repositories.postgres.cv_version_repository import PostgresCVVersionRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.clarification import ClarificationQuestionStatus
from app.schemas.cover_letter import (
    CoverLetterLength,
    CoverLetterResponse,
    CoverLetterStatus,
    CoverLetterSummary,
    CoverLetterTone,
    FactualClaimItem,
    GenerateCoverLetterRequest,
    RegenerateCoverLetterRequest,
    StructuredCoverLetterOutput,
    UpdateCoverLetterRequest,
)
from app.services.clarification_service import ClarificationService

logger = get_logger("app.services.cover_letter_service")


class CoverLetterService:
    """
    Service coordinating evidence-grounded cover letter generation,
    transparent factual provenance auditing, editing, versioning, and lifecycle management.
    """

    def __init__(
        self,
        session: AsyncSession,
        cover_letter_repo: Optional[ICoverLetterRepository] = None,
        job_repo: Optional[IJobTargetRepository] = None,
        cv_version_repo: Optional[ICVVersionRepository] = None,
        profile_repo: Optional[IProfileRepository] = None,
        clarification_service: Optional[ClarificationService] = None,
        ai_provider: Optional[AIProviderInterface] = None,
    ) -> None:
        self.session = session
        self.cover_letter_repo = cover_letter_repo or PostgresCoverLetterRepository(session)
        self.job_repo = job_repo or PostgresJobTargetRepository(session)
        self.cv_version_repo = cv_version_repo or PostgresCVVersionRepository(session)
        self.profile_repo = profile_repo or PostgresProfileRepository(session)
        self.clarification_service = clarification_service or ClarificationService(
            job_target_repository=self.job_repo,
            profile_repository=self.profile_repo,
        )
        self.ai_provider = ai_provider or get_ai_provider()

    async def generate_cover_letter(
        self,
        user_id: Union[uuid.UUID, str],
        request: GenerateCoverLetterRequest,
    ) -> CoverLetterResponse:
        """
        Generate an evidence-grounded cover letter tailored to a saved job target.
        Strict zero-hallucination constraint: only asserts confirmed candidate profile facts,
        metrics, and confirmed clarification answers.
        """
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id

        # 1. Fetch and authorize target job
        job = await self.job_repo.get_by_id(job_id=request.job_id, user_id=uid)
        if not job:
            raise NotFoundError(
                message="Target job not found or you do not have permission to access it.",
                code="JOB_NOT_FOUND",
            )

        # 2. Fetch and authorize optional contextual CVVersion
        cv_version: Optional[CVVersion] = None
        if request.cv_version_id:
            cv_version = await self.cv_version_repo.get_by_id(
                version_id=request.cv_version_id,
                user_id=uid,
            )
            if not cv_version:
                raise NotFoundError(
                    message="Referenced CV version not found or belongs to another user.",
                    code="CV_VERSION_NOT_FOUND",
                )

        # 3. Fetch candidate profile
        profile = await self.profile_repo.get_by_user_id(user_id=uid)
        if not profile:
            raise NotFoundError(
                message="Candidate profile not found. Please set up your profile first.",
                code="PROFILE_NOT_FOUND",
            )

        # 4. Fetch confirmed clarifications for this job
        clarification_session = await self.clarification_service.get_or_create_session(
            user_id=uid,
            job_id=job.id,
        )
        answered_clarifications = [
            q for q in clarification_session.questions
            if q.status == ClarificationQuestionStatus.ANSWERED and q.answer
        ]

        # 5. Build Candidate Facts and Evidence Trace
        candidate_name = self._resolve_candidate_name(profile)
        sender_contact = self._resolve_candidate_contact(profile)

        # 6. Extract Requirements and Identify Gaps
        analysis = job.analysis_result or {}
        requirements = analysis.get("requirements", [])
        mandatory_gaps: List[str] = []
        preferred_gaps: List[str] = []

        for req in requirements:
            req_text = req.get("requirement", "")
            match_status = req.get("candidate_match_status", "missing")
            is_mand = req.get("is_mandatory", True)

            addressed = any(
                c.requirement_text.lower() == req_text.lower()
                for c in answered_clarifications
            )

            if match_status in ("missing", "unverified") and not addressed:
                if is_mand:
                    mandatory_gaps.append(req_text)
                else:
                    preferred_gaps.append(req_text)

        all_unsupported_gaps = mandatory_gaps + preferred_gaps

        # 7. Build AI Prompt
        prompt = self._build_generation_prompt(
            job=job,
            profile=profile,
            cv_version=cv_version,
            answered_clarifications=answered_clarifications,
            req=request,
            unsupported_gaps=all_unsupported_gaps,
        )

        system_instruction = (
            "You are an expert executive career strategist and professional cover letter writer. "
            "STRICT OPERATING PRINCIPLES:\n"
            "1. ZERO FABRICATION: You must strictly restrict all factual statements, metrics, company names, "
            "degrees, employment dates, and skill assertions to the provided Candidate Profile and confirmed clarifications. "
            "NEVER invent outside achievements, percentages, awards, or previous employers.\n"
            "2. EVIDENCE GROUNDING: For every major achievement stated in the body paragraphs, cite the exact source in factual_claims.\n"
            "3. UNRESOLVED GAPS: If the job requires a skill or qualification that the candidate lacks verified evidence for, "
            "do NOT invent or falsely claim it. Record it in 'unresolved_gaps' and use neutral, adaptive language.\n"
            "4. TONE & STRUCTURE: Follow the requested tone and length precisely. Produce a compelling opening identifying the role, "
            "2-3 substantive body paragraphs demonstrating relevant value, and a professional closing with a clear call-to-action."
        )

        # 8. Generate structured output
        try:
            structured_output: StructuredCoverLetterOutput = await self.ai_provider.generate_structured(
                prompt=prompt,
                schema=StructuredCoverLetterOutput,
                system_instruction=system_instruction,
                temperature=0.1,
            )
        except Exception as exc:
            logger.error("AI generation for cover letter failed", exc_info=exc)
            raise BadRequestError(
                message=f"Failed to generate cover letter: {str(exc)}",
                code="COVER_LETTER_GENERATION_FAILED",
            )

        # 9. Format recipient and header
        rec_name = request.recipient_name or "Hiring Manager"
        rec_company = request.recipient_company or job.company_name
        rec_title = request.recipient_title or "Hiring Team"
        rec_address = request.recipient_address or job.location

        full_content = self._format_full_content(
            sender_name=candidate_name,
            sender_contact=sender_contact,
            recipient_name=rec_name,
            recipient_title=rec_title,
            recipient_company=rec_company,
            recipient_address=rec_address,
            salutation=structured_output.salutation,
            opening=structured_output.opening,
            body_paragraphs=structured_output.body_paragraphs,
            closing=structured_output.closing,
            sign_off=structured_output.sign_off,
        )

        # 10. Persist CoverLetter record
        letter_name = request.name or f"{job.title} at {job.company_name} - Cover Letter"
        cover_letter = CoverLetter(
            id=uuid.uuid4(),
            user_id=uid,
            job_target_id=job.id,
            cv_version_id=cv_version.id if cv_version else None,
            name=letter_name,
            status=CoverLetterStatus.DRAFT.value,
            tone=request.tone.value,
            length_option=request.length_option.value,
            recipient_name=rec_name,
            recipient_title=rec_title,
            recipient_company=rec_company,
            recipient_address=rec_address,
            salutation=structured_output.salutation,
            opening=structured_output.opening,
            body_paragraphs=structured_output.body_paragraphs,
            closing=structured_output.closing,
            sign_off=structured_output.sign_off,
            sender_name=candidate_name,
            sender_contact=sender_contact,
            full_content=full_content,
            factual_claims=[c.model_dump() for c in structured_output.factual_claims],
            unresolved_gaps=structured_output.unresolved_gaps or all_unsupported_gaps,
            change_summary=structured_output.change_summary or "Initial tailored draft generated from verified candidate profile evidence.",
            generation_parameters={
                "tone": request.tone.value,
                "length_option": request.length_option.value,
                "additional_instructions": request.additional_instructions,
                "cv_version_id": str(request.cv_version_id) if request.cv_version_id else None,
            },
        )

        saved = await self.cover_letter_repo.create(cover_letter)
        logger.info(f"Evidence-grounded cover letter {saved.id} created successfully for user {uid}")
        return self._to_response(saved)

    async def regenerate_cover_letter(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
        request: RegenerateCoverLetterRequest,
    ) -> CoverLetterResponse:
        """
        Regenerate an existing cover letter with adjusted tone, length, or candidate instructions.
        When preserve_as_new_version=True, creates a new independent version record, preserving history.
        """
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        lid = uuid.UUID(str(letter_id)) if isinstance(letter_id, str) else letter_id

        existing = await self.cover_letter_repo.get_by_id(letter_id=lid, user_id=uid)
        if not existing:
            raise NotFoundError(
                message="Cover letter not found or you do not have permission to access it.",
                code="COVER_LETTER_NOT_FOUND",
            )

        # Resolve associated job and profile
        job: Optional[JobTarget] = None
        if existing.job_target_id:
            job = await self.job_repo.get_by_id(job_id=existing.job_target_id, user_id=uid)

        profile = await self.profile_repo.get_by_user_id(user_id=uid)
        if not profile:
            raise NotFoundError(message="Candidate profile not found.", code="PROFILE_NOT_FOUND")

        # Resolve target tone and length
        new_tone = request.tone or CoverLetterTone(existing.tone)
        new_length = request.length_option or CoverLetterLength(existing.length_option)
        new_instructions = request.additional_instructions or existing.generation_parameters.get("additional_instructions")

        # Clarifications
        answered_clarifications = []
        if job:
            clar_session = await self.clarification_service.get_or_create_session(user_id=uid, job_id=job.id)
            answered_clarifications = [
                q for q in clar_session.questions
                if q.status == ClarificationQuestionStatus.ANSWERED and q.answer
            ]

        # Build regeneration prompt
        gen_req = GenerateCoverLetterRequest(
            job_id=existing.job_target_id or uuid.uuid4(),
            cv_version_id=existing.cv_version_id,
            tone=new_tone,
            length_option=new_length,
            additional_instructions=new_instructions,
            recipient_name=existing.recipient_name,
            recipient_title=existing.recipient_title,
            recipient_company=existing.recipient_company,
            recipient_address=existing.recipient_address,
        )

        prompt = self._build_generation_prompt(
            job=job,
            profile=profile,
            cv_version=existing.cv_version,
            answered_clarifications=answered_clarifications,
            req=gen_req,
            unsupported_gaps=existing.unresolved_gaps or [],
            existing_letter=existing,
        )

        system_instruction = (
            "You are revising and polishing an existing evidence-grounded cover letter. "
            "STRICT RULES:\n"
            "1. Zero fabrication: Do not invent any new claims.\n"
            "2. Apply the requested tone and instructions.\n"
            "3. Clearly document what was changed in 'change_summary'."
        )

        try:
            structured_output: StructuredCoverLetterOutput = await self.ai_provider.generate_structured(
                prompt=prompt,
                schema=StructuredCoverLetterOutput,
                system_instruction=system_instruction,
                temperature=0.15,
            )
        except Exception as exc:
            logger.error("AI regeneration for cover letter failed", exc_info=exc)
            raise BadRequestError(
                message=f"Failed to regenerate cover letter: {str(exc)}",
                code="COVER_LETTER_REGENERATION_FAILED",
            )

        full_content = self._format_full_content(
            sender_name=existing.sender_name,
            sender_contact=existing.sender_contact,
            recipient_name=existing.recipient_name or "Hiring Manager",
            recipient_title=existing.recipient_title or "Hiring Team",
            recipient_company=existing.recipient_company or (job.company_name if job else "Company"),
            recipient_address=existing.recipient_address or (job.location if job else ""),
            salutation=structured_output.salutation,
            opening=structured_output.opening,
            body_paragraphs=structured_output.body_paragraphs,
            closing=structured_output.closing,
            sign_off=structured_output.sign_off,
        )

        change_summary_text = (
            structured_output.change_summary
            or f"Regenerated in {new_tone.value} tone with {new_length.value} length based on updated candidate criteria."
        )

        if request.preserve_as_new_version:
            # Create independent new version
            new_name = request.new_name or f"{existing.name} (Rev)"
            new_letter = CoverLetter(
                id=uuid.uuid4(),
                user_id=uid,
                job_target_id=existing.job_target_id,
                cv_version_id=existing.cv_version_id,
                name=new_name,
                status=CoverLetterStatus.DRAFT.value,
                tone=new_tone.value,
                length_option=new_length.value,
                recipient_name=existing.recipient_name,
                recipient_title=existing.recipient_title,
                recipient_company=existing.recipient_company,
                recipient_address=existing.recipient_address,
                salutation=structured_output.salutation,
                opening=structured_output.opening,
                body_paragraphs=structured_output.body_paragraphs,
                closing=structured_output.closing,
                sign_off=structured_output.sign_off,
                sender_name=existing.sender_name,
                sender_contact=existing.sender_contact,
                full_content=full_content,
                factual_claims=[c.model_dump() for c in structured_output.factual_claims],
                unresolved_gaps=structured_output.unresolved_gaps or existing.unresolved_gaps,
                change_summary=change_summary_text,
                generation_parameters={
                    "tone": new_tone.value,
                    "length_option": new_length.value,
                    "additional_instructions": new_instructions,
                    "parent_letter_id": str(existing.id),
                },
            )
            saved = await self.cover_letter_repo.create(new_letter)
            logger.info(f"Preserved regenerated cover letter as new version {saved.id} (parent: {existing.id})")
            return self._to_response(saved)
        else:
            # Update existing letter in place
            existing.tone = new_tone.value
            existing.length_option = new_length.value
            existing.salutation = structured_output.salutation
            existing.opening = structured_output.opening
            existing.body_paragraphs = structured_output.body_paragraphs
            existing.closing = structured_output.closing
            existing.sign_off = structured_output.sign_off
            existing.full_content = full_content
            existing.factual_claims = [c.model_dump() for c in structured_output.factual_claims]
            existing.unresolved_gaps = structured_output.unresolved_gaps or existing.unresolved_gaps
            existing.change_summary = change_summary_text
            existing.generation_parameters = {
                **existing.generation_parameters,
                "tone": new_tone.value,
                "length_option": new_length.value,
                "additional_instructions": new_instructions,
            }
            updated = await self.cover_letter_repo.update(existing)
            logger.info(f"Updated existing cover letter draft {updated.id} in-place")
            return self._to_response(updated)

    async def update_cover_letter(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
        request: UpdateCoverLetterRequest,
    ) -> CoverLetterResponse:
        """Update editable fields on a cover letter."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        lid = uuid.UUID(str(letter_id)) if isinstance(letter_id, str) else letter_id
        letter = await self.cover_letter_repo.get_by_id(letter_id=lid, user_id=uid)
        if not letter:
            raise NotFoundError(
                message="Cover letter not found or you do not have permission to access it.",
                code="COVER_LETTER_NOT_FOUND",
            )

        if request.name is not None:
            letter.name = request.name.strip()
        if request.status is not None:
            letter.status = request.status.value
        if request.tone is not None:
            letter.tone = request.tone.value
        if request.length_option is not None:
            letter.length_option = request.length_option.value
        if request.recipient_name is not None:
            letter.recipient_name = request.recipient_name
        if request.recipient_title is not None:
            letter.recipient_title = request.recipient_title
        if request.recipient_company is not None:
            letter.recipient_company = request.recipient_company
        if request.recipient_address is not None:
            letter.recipient_address = request.recipient_address
        if request.salutation is not None:
            letter.salutation = request.salutation
        if request.opening is not None:
            letter.opening = request.opening
        if request.body_paragraphs is not None:
            letter.body_paragraphs = request.body_paragraphs
        if request.closing is not None:
            letter.closing = request.closing
        if request.sign_off is not None:
            letter.sign_off = request.sign_off
        if request.sender_name is not None:
            letter.sender_name = request.sender_name
        if request.sender_contact is not None:
            letter.sender_contact = request.sender_contact

        # Re-synthesize full content if provided directly or reconstructed from parts
        if request.full_content is not None:
            letter.full_content = request.full_content
        else:
            letter.full_content = self._format_full_content(
                sender_name=letter.sender_name,
                sender_contact=letter.sender_contact,
                recipient_name=letter.recipient_name or "",
                recipient_title=letter.recipient_title or "",
                recipient_company=letter.recipient_company or "",
                recipient_address=letter.recipient_address or "",
                salutation=letter.salutation,
                opening=letter.opening,
                body_paragraphs=letter.body_paragraphs,
                closing=letter.closing,
                sign_off=letter.sign_off,
            )

        updated = await self.cover_letter_repo.update(letter)
        return self._to_response(updated)

    async def duplicate_cover_letter(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> CoverLetterResponse:
        """Duplicate an existing cover letter as an independent new draft."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        lid = uuid.UUID(str(letter_id)) if isinstance(letter_id, str) else letter_id
        original = await self.cover_letter_repo.get_by_id(letter_id=lid, user_id=uid)
        if not original:
            raise NotFoundError(
                message="Cover letter not found or you do not have permission to access it.",
                code="COVER_LETTER_NOT_FOUND",
            )

        clone = CoverLetter(
            id=uuid.uuid4(),
            user_id=uid,
            job_target_id=original.job_target_id,
            cv_version_id=original.cv_version_id,
            name=f"{original.name} (Copy)",
            status=CoverLetterStatus.DRAFT.value,
            tone=original.tone,
            length_option=original.length_option,
            recipient_name=original.recipient_name,
            recipient_title=original.recipient_title,
            recipient_company=original.recipient_company,
            recipient_address=original.recipient_address,
            salutation=original.salutation,
            opening=original.opening,
            body_paragraphs=list(original.body_paragraphs),
            closing=original.closing,
            sign_off=original.sign_off,
            sender_name=original.sender_name,
            sender_contact=original.sender_contact,
            full_content=original.full_content,
            factual_claims=list(original.factual_claims),
            unresolved_gaps=list(original.unresolved_gaps),
            change_summary=f"Cloned from {original.name}.",
            generation_parameters=dict(original.generation_parameters),
        )

        saved = await self.cover_letter_repo.create(clone)
        return self._to_response(saved)

    async def delete_cover_letter(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> None:
        """Delete a cover letter with strict ownership enforcement."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        lid = uuid.UUID(str(letter_id)) if isinstance(letter_id, str) else letter_id
        letter = await self.cover_letter_repo.get_by_id(letter_id=lid, user_id=uid)
        if not letter:
            raise NotFoundError(
                message="Cover letter not found or you do not have permission to access it.",
                code="COVER_LETTER_NOT_FOUND",
            )
        await self.cover_letter_repo.delete(letter)
        logger.info(f"Deleted cover letter {lid} for user {uid}")

    async def get_cover_letter(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> CoverLetterResponse:
        """Retrieve single cover letter with relationship details."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        lid = uuid.UUID(str(letter_id)) if isinstance(letter_id, str) else letter_id
        letter = await self.cover_letter_repo.get_by_id(letter_id=lid, user_id=uid)
        if not letter:
            raise NotFoundError(
                message="Cover letter not found or you do not have permission to access it.",
                code="COVER_LETTER_NOT_FOUND",
            )
        return self._to_response(letter)

    async def list_cover_letters(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        job_target_id: Optional[Union[uuid.UUID, str]] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[CoverLetterSummary], int]:
        """List user cover letters with pagination and filters."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
        jid = uuid.UUID(str(job_target_id)) if (job_target_id and isinstance(job_target_id, str)) else job_target_id
        letters, total = await self.cover_letter_repo.list_by_user(
            user_id=uid,
            status=status,
            job_target_id=jid,
            search=search,
            limit=limit,
            offset=offset,
        )

        summaries = [
            CoverLetterSummary(
                id=cl.id,
                name=cl.name,
                status=CoverLetterStatus(cl.status),
                tone=CoverLetterTone(cl.tone),
                length_option=CoverLetterLength(cl.length_option),
                job_target_id=cl.job_target_id,
                job_target_title=cl.job_target.title if cl.job_target else None,
                job_target_company=cl.job_target.company_name if cl.job_target else None,
                cv_version_id=cl.cv_version_id,
                cv_version_name=cl.cv_version.name if cl.cv_version else None,
                word_count=len(cl.full_content.split()) if cl.full_content else 0,
                created_at=cl.created_at,
                updated_at=cl.updated_at,
            )
            for cl in letters
        ]
        return summaries, total

    # -------------------------------------------------------------------------
    # Helper & Formatting Methods
    # -------------------------------------------------------------------------

    def _resolve_candidate_name(self, profile: CandidateProfile) -> str:
        """Resolve full candidate name."""
        name_parts = [profile.first_name, profile.last_name]
        full = " ".join([p for p in name_parts if p]).strip()
        if full:
            return full
        if profile.preferred_name:
            return profile.preferred_name
        return "Candidate"

    def _resolve_candidate_contact(self, profile: CandidateProfile) -> str:
        """Format candidate contact line (email, phone, location)."""
        parts = []
        if profile.email:
            parts.append(profile.email)
        if profile.phone:
            parts.append(profile.phone)
        if profile.city:
            loc = profile.city
            if profile.country:
                loc += f", {profile.country}"
            parts.append(loc)
        return " · ".join(parts) if parts else ""

    def _format_full_content(
        self,
        sender_name: str,
        sender_contact: Optional[str],
        recipient_name: str,
        recipient_title: str,
        recipient_company: str,
        recipient_address: Optional[str],
        salutation: str,
        opening: str,
        body_paragraphs: List[str],
        closing: str,
        sign_off: str,
    ) -> str:
        """Construct full standardized plain text cover letter with header blocks."""
        today_str = datetime.date.today().strftime("%B %d, %Y")

        lines: List[str] = []
        lines.append(sender_name)
        if sender_contact:
            lines.append(sender_contact)
        lines.append("")
        lines.append(today_str)
        lines.append("")

        if recipient_name:
            lines.append(recipient_name)
        if recipient_title:
            lines.append(recipient_title)
        if recipient_company:
            lines.append(recipient_company)
        if recipient_address:
            lines.append(recipient_address)
        lines.append("")

        lines.append(salutation)
        lines.append("")

        lines.append(opening)
        lines.append("")

        for p in body_paragraphs:
            if p.strip():
                lines.append(p.strip())
                lines.append("")

        lines.append(closing)
        lines.append("")

        lines.append(sign_off)
        lines.append(sender_name)

        return "\n".join(lines)

    def _build_generation_prompt(
        self,
        job: Optional[JobTarget],
        profile: CandidateProfile,
        cv_version: Optional[CVVersion],
        answered_clarifications: List[Any],
        req: GenerateCoverLetterRequest,
        unsupported_gaps: List[str],
        existing_letter: Optional[CoverLetter] = None,
    ) -> str:
        """Assemble structured prompt for cover letter generation with evidence bounds."""
        lines: List[str] = []

        # Target Role & Company
        if job:
            lines.append(f"TARGET ROLE: {job.title}")
            lines.append(f"TARGET COMPANY: {job.company_name}")
            if job.location:
                lines.append(f"TARGET LOCATION: {job.location}")
            if job.employment_type:
                lines.append(f"EMPLOYMENT TYPE: {job.employment_type}")
        else:
            lines.append("TARGET ROLE: Software Engineer")
            lines.append("TARGET COMPANY: Target Organization")

        rec_name = req.recipient_name or (job.company_name if job else "Hiring Team")
        lines.append(f"RECIPIENT: {rec_name}")

        # Configuration
        lines.append(f"REQUESTED TONE: {req.tone.value}")
        lines.append(f"REQUESTED LENGTH: {req.length_option.value}")

        if req.additional_instructions:
            lines.append(f"CANDIDATE INSTRUCTIONS: {req.additional_instructions}")

        # Candidate Evidence Pool
        lines.append("\n--- VERIFIED CANDIDATE PROFILE EVIDENCE (SOURCE OF TRUTH) ---")
        lines.append(f"NAME: {self._resolve_candidate_name(profile)}")
        if profile.primary_title:
            lines.append(f"HEADLINE: {profile.primary_title}")
        if profile.base_summary:
            lines.append(f"SUMMARY: {profile.base_summary}")

        # Skills
        skill_names = [s.name for s in (profile.skills or []) if s.name]
        if skill_names:
            lines.append(f"CANDIDATE SKILLS: {', '.join(skill_names)}")

        # Work Experience & Accomplishments
        lines.append("\nWORK EXPERIENCE ACCOMPLISHMENTS:")
        for exp in (profile.experiences or []):
            comp = exp.company or "Company"
            role = getattr(exp, "position", None) or getattr(exp, "job_title", None) or "Role"
            dates = f"{exp.start_date or ''} - {exp.end_date or 'Present'}"
            lines.append(f"- {role} at {comp} ({dates}):")
            if exp.description:
                lines.append(f"  Description: {exp.description}")
            for resp in (exp.responsibilities or []):
                lines.append(f"  * {resp}")
            for acc in (exp.achievements or []):
                if isinstance(acc, str):
                    lines.append(f"  * {acc}")
                elif hasattr(acc, "description"):
                    metric_str = f" [Metric: {acc.metric_value} {acc.metric_type}]" if getattr(acc, "metric_value", None) else ""
                    lines.append(f"  * {acc.description}{metric_str}")

        # Projects
        if profile.projects:
            lines.append("\nKEY PROJECTS:")
            for proj in profile.projects:
                techs = f" (Tech: {', '.join(proj.technologies)})" if proj.technologies else ""
                lines.append(f"- {proj.name}{techs}: {proj.description or ''}")

        # Confirmed clarifications
        if answered_clarifications:
            lines.append("\nCANDIDATE-CONFIRMED CLARIFICATIONS:")
            for clar in answered_clarifications:
                lines.append(f"- Q: {clar.requirement_text} -> A: {clar.answer}")

        # Job Requirements & Analysis
        if job and job.analysis_result:
            reqs = job.analysis_result.get("requirements", [])
            lines.append("\nTARGET JOB REQUIREMENTS:")
            for r in reqs[:12]:
                mand_str = "MANDATORY" if r.get("is_mandatory", True) else "PREFERRED"
                lines.append(f"- [{mand_str}] {r.get('requirement', '')}")

        # Unsupported Gaps
        if unsupported_gaps:
            lines.append(f"\nUNRESOLVED GAPS (NO VERIFIED EVIDENCE - DO NOT CLAIM): {', '.join(unsupported_gaps[:10])}")
        else:
            lines.append("\nUNRESOLVED GAPS: None")

        # Existing letter context if regenerating
        if existing_letter:
            lines.append("\nPREVIOUS LETTER DRAFT FOR REVISION:")
            lines.append(existing_letter.full_content)

        return "\n".join(lines)

    def _to_response(self, letter: CoverLetter) -> CoverLetterResponse:
        """Convert CoverLetter ORM model to Pydantic CoverLetterResponse."""
        return CoverLetterResponse(
            id=letter.id,
            user_id=letter.user_id,
            job_target_id=letter.job_target_id,
            job_target_title=letter.job_target.title if letter.job_target else None,
            job_target_company=letter.job_target.company_name if letter.job_target else None,
            cv_version_id=letter.cv_version_id,
            cv_version_name=letter.cv_version.name if letter.cv_version else None,
            name=letter.name,
            status=CoverLetterStatus(letter.status),
            tone=CoverLetterTone(letter.tone),
            length_option=CoverLetterLength(letter.length_option),
            recipient_name=letter.recipient_name,
            recipient_title=letter.recipient_title,
            recipient_company=letter.recipient_company,
            recipient_address=letter.recipient_address,
            salutation=letter.salutation,
            opening=letter.opening,
            body_paragraphs=list(letter.body_paragraphs),
            closing=letter.closing,
            sign_off=letter.sign_off,
            sender_name=letter.sender_name,
            sender_contact=letter.sender_contact,
            full_content=letter.full_content,
            word_count=len(letter.full_content.split()) if letter.full_content else 0,
            factual_claims=[
                FactualClaimItem.model_validate(c)
                if isinstance(c, dict) else c
                for c in (letter.factual_claims or [])
            ],
            unresolved_gaps=list(letter.unresolved_gaps or []),
            change_summary=letter.change_summary,
            generation_parameters=dict(letter.generation_parameters or {}),
            created_at=letter.created_at,
            updated_at=letter.updated_at,
        )
