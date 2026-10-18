from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional, Union
import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.models.job_target import JobTarget
from app.models.profile import CandidateProfile, CandidateSkill, EvidenceItem
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.clarification import (
    ClarificationAnswerRequest,
    ClarificationBulkAnswerRequest,
    ClarificationPromoteRequest,
    ClarificationQuestionItem,
    ClarificationQuestionStatus,
    ClarificationSessionResponse,
)

logger = get_logger("app.services.clarification_service")


class ClarificationService:
    """
    Service managing prioritized clarification questions and resumable sessions.
    - Generates actionable questions for missing, partial, or unverified requirements.
    - Prioritizes mandatory job requirements over preferred ones.
    - Persists answers in the job target without mutating master candidate profile.
    - Supports optional, candidate-confirmed promotion to the candidate knowledge base.
    """

    def __init__(
        self,
        job_target_repository: IJobTargetRepository,
        profile_repository: IProfileRepository,
    ) -> None:
        self.job_repo = job_target_repository
        self.profile_repo = profile_repository

    async def get_or_create_session(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> ClarificationSessionResponse:
        """
        Retrieve existing clarification session or initialize a fresh prioritized session
        based on the target job's evidence analysis.
        """
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )

        existing_data = job.clarification_data or {}
        existing_questions_raw = existing_data.get("questions", [])

        # If existing questions exist, map by ID to preserve answers
        existing_map: Dict[str, ClarificationQuestionItem] = {}
        for q_dict in existing_questions_raw:
            try:
                item = ClarificationQuestionItem.model_validate(q_dict)
                existing_map[item.id] = item
            except Exception as e:
                logger.warning(f"Failed to parse existing clarification item: {e}")

        # Generate / merge questions from analysis requirements
        analysis_result = job.analysis_result or {}
        requirements_raw = analysis_result.get("requirements", [])

        generated_questions: List[ClarificationQuestionItem] = []

        for req in requirements_raw:
            match_status = req.get("candidate_match_status", "missing")
            gap_type = req.get("gap_type")
            is_mandatory = req.get("is_mandatory", True)
            category = req.get("category", "skills")
            req_text = req.get("requirement", "").strip()

            if not req_text:
                continue

            # Check if this requirement needs clarification (missing, unverified, partial, or has a gap)
            needs_clarification = (
                match_status in ("missing", "unverified", "partial")
                or gap_type in ("absent_from_profile", "unverified_claim", "skill_gap")
            )

            if not needs_clarification:
                continue

            # Deterministic question ID based on job ID and requirement text
            q_id = hashlib.sha256(f"{job.id}:{req_text.lower()}".encode("utf-8")).hexdigest()[:12]

            # If already answered or existing, preserve user's progress
            if q_id in existing_map:
                existing_item = existing_map[q_id]
                generated_questions.append(existing_item)
                continue

            # Formulate tailored, actionable question
            question_text, context_text = self._formulate_question(
                category=category,
                requirement=req_text,
                is_mandatory=is_mandatory,
                match_status=match_status,
                gap_type=gap_type,
                job_title=job.title,
                company_name=job.company_name,
            )

            priority = 1 if is_mandatory else 2

            new_q = ClarificationQuestionItem(
                id=q_id,
                job_id=job.id,
                requirement_id=uuid.UUID(req["id"]) if req.get("id") else None,
                requirement_text=req_text,
                is_mandatory=is_mandatory,
                category=category,
                gap_type=gap_type,
                question=question_text,
                context=context_text,
                status=ClarificationQuestionStatus.UNANSWERED,
                priority=priority,
                provenance="candidate_clarification",
                verification_status="unverified",
            )
            generated_questions.append(new_q)

        # Fallback if no structured requirements were extracted, but missing keywords/gaps exist
        if not generated_questions:
            kw_summary = analysis_result.get("keyword_summary", {})
            fallback_items = kw_summary.get("top_missing_keywords", []) or kw_summary.get("identified_gaps", [])
            for item_text in fallback_items:
                item_text = item_text.strip()
                if not item_text:
                    continue
                q_id = hashlib.sha256(f"{job.id}:{item_text.lower()}".encode("utf-8")).hexdigest()[:12]
                if q_id in existing_map:
                    generated_questions.append(existing_map[q_id])
                    continue
                question_text, context_text = self._formulate_question(
                    category="skills",
                    requirement=item_text,
                    is_mandatory=True,
                    match_status="missing",
                    gap_type="skill_gap",
                    job_title=job.title,
                    company_name=job.company_name,
                )
                new_q = ClarificationQuestionItem(
                    id=q_id,
                    job_id=job.id,
                    requirement_id=None,
                    requirement_text=item_text,
                    is_mandatory=True,
                    category="skills",
                    gap_type="skill_gap",
                    question=question_text,
                    context=context_text,
                    status=ClarificationQuestionStatus.UNANSWERED,
                    priority=1,
                    provenance="candidate_clarification",
                    verification_status="unverified",
                )
                generated_questions.append(new_q)

        # Sort questions: Priority 1 (mandatory) first, then Priority 2 (preferred)
        generated_questions.sort(key=lambda q: (q.priority, 0 if q.status == ClarificationQuestionStatus.UNANSWERED else 1))

        # Cap questions to top 10 most critical to keep cognitive load low
        final_questions = generated_questions[:10]

        answered_count = sum(1 for q in final_questions if q.status == ClarificationQuestionStatus.ANSWERED)
        skipped_count = sum(1 for q in final_questions if q.status == ClarificationQuestionStatus.SKIPPED)
        unanswered_count = sum(1 for q in final_questions if q.status == ClarificationQuestionStatus.UNANSWERED)
        total_questions = len(final_questions)
        is_completed = total_questions > 0 and (answered_count + skipped_count) == total_questions

        session_response = ClarificationSessionResponse(
            job_id=job.id,
            job_title=job.title,
            company_name=job.company_name,
            total_questions=total_questions,
            answered_count=answered_count,
            skipped_count=skipped_count,
            unanswered_count=unanswered_count,
            is_completed=is_completed,
            questions=final_questions,
            updated_at=datetime.now(timezone.utc),
        )

        # Save session onto JobTarget record
        job.clarification_data = session_response.model_dump(mode="json")
        await self.job_repo.update(job)

        return session_response

    async def answer_question(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
        question_id: str,
        data: ClarificationAnswerRequest,
    ) -> ClarificationSessionResponse:
        """Submit candidate answer for a specific clarification question."""
        session = await self.get_or_create_session(user_id=user_id, job_id=job_id)
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError("Job target not found.")

        matched_q: Optional[ClarificationQuestionItem] = None
        for q in session.questions:
            if q.id == question_id:
                matched_q = q
                q.answer = data.answer.strip()
                q.status = ClarificationQuestionStatus.ANSWERED
                q.answered_at = datetime.now(timezone.utc)
                q.save_to_profile = data.save_to_profile
                break

        if not matched_q:
            raise NotFoundError(f"Clarification question '{question_id}' not found in session.")

        # Recalculate metrics
        session.answered_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.ANSWERED)
        session.skipped_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.SKIPPED)
        session.unanswered_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.UNANSWERED)
        session.is_completed = (session.answered_count + session.skipped_count) == session.total_questions
        session.updated_at = datetime.now(timezone.utc)

        # Optional: candidate-confirmed promotion to candidate profile
        if data.save_to_profile and matched_q.answer:
            await self._promote_claim_to_profile(
                user_id=user_id,
                requirement=matched_q.requirement_text,
                answer=matched_q.answer,
                category=matched_q.category,
            )

        # Persist updated session
        job.clarification_data = session.model_dump(mode="json")
        await self.job_repo.update(job)

        return session

    async def skip_question(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
        question_id: str,
    ) -> ClarificationSessionResponse:
        """Mark a question as skipped."""
        session = await self.get_or_create_session(user_id=user_id, job_id=job_id)
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError("Job target not found.")

        found = False
        for q in session.questions:
            if q.id == question_id:
                q.status = ClarificationQuestionStatus.SKIPPED
                found = True
                break

        if not found:
            raise NotFoundError(f"Clarification question '{question_id}' not found in session.")

        session.answered_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.ANSWERED)
        session.skipped_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.SKIPPED)
        session.unanswered_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.UNANSWERED)
        session.is_completed = (session.answered_count + session.skipped_count) == session.total_questions
        session.updated_at = datetime.now(timezone.utc)

        job.clarification_data = session.model_dump(mode="json")
        await self.job_repo.update(job)

        return session

    async def bulk_answer(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
        data: ClarificationBulkAnswerRequest,
    ) -> ClarificationSessionResponse:
        """Submit multiple answers in a single request."""
        session = await self.get_or_create_session(user_id=user_id, job_id=job_id)
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError("Job target not found.")

        for q in session.questions:
            if q.id in data.answers:
                answer_text = data.answers[q.id].strip()
                if answer_text:
                    q.answer = answer_text
                    q.status = ClarificationQuestionStatus.ANSWERED
                    q.answered_at = datetime.now(timezone.utc)
                    q.save_to_profile = data.save_to_profile

                    if data.save_to_profile:
                        await self._promote_claim_to_profile(
                            user_id=user_id,
                            requirement=q.requirement_text,
                            answer=answer_text,
                            category=q.category,
                        )

        session.answered_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.ANSWERED)
        session.skipped_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.SKIPPED)
        session.unanswered_count = sum(1 for q in session.questions if q.status == ClarificationQuestionStatus.UNANSWERED)
        session.is_completed = (session.answered_count + session.skipped_count) == session.total_questions
        session.updated_at = datetime.now(timezone.utc)

        job.clarification_data = session.model_dump(mode="json")
        await self.job_repo.update(job)

        return session

    async def promote_answer_to_profile(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
        question_id: str,
        data: ClarificationPromoteRequest,
    ) -> Dict[str, Any]:
        """Candidate-confirmed action to persist an answered question into the candidate knowledge base."""
        session = await self.get_or_create_session(user_id=user_id, job_id=job_id)

        target_q: Optional[ClarificationQuestionItem] = None
        for q in session.questions:
            if q.id == question_id:
                target_q = q
                break

        if not target_q:
            raise NotFoundError("Clarification question not found.")
        if not target_q.answer:
            raise BadRequestError("Cannot promote an unanswered clarification question.")

        result = await self._promote_claim_to_profile(
            user_id=user_id,
            requirement=target_q.requirement_text,
            answer=target_q.answer,
            category=data.category or target_q.category,
        )

        target_q.save_to_profile = True
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if job:
            job.clarification_data = session.model_dump(mode="json")
            await self.job_repo.update(job)

        return result

    async def _promote_claim_to_profile(
        self,
        user_id: Union[uuid.UUID, str],
        requirement: str,
        answer: str,
        category: str,
    ) -> Dict[str, Any]:
        """
        Internal safe promotion creating an unverified CandidateSkill or Evidence record
        with explicit provenance 'candidate_clarification'.
        """
        profile = await self.profile_repo.get_by_user_id(user_id=user_id)
        if not profile:
            return {"status": "skipped", "reason": "No profile found"}

        # 1. Create candidate evidence record
        evidence = EvidenceItem(
            profile_id=profile.id,
            title=f"Clarification: {requirement}",
            description=answer,
            source="candidate_clarification",
            source_type="user_claim",
            verification_status="unverified",
            notes="Added via candidate confirmation during job-specific clarification session.",
            provenance="candidate_clarification",
        )
        await self.profile_repo.create_evidence(evidence)

        # 2. If it's a technical skill / tool and not already in profile skills, add it safely
        if category in ("skills", "technologies"):
            existing_skill = await self.profile_repo.get_skill_by_name(profile.id, requirement)
            clean_skill_name = requirement.strip()
            if not existing_skill and len(clean_skill_name) <= 60:
                new_skill = CandidateSkill(
                    profile_id=profile.id,
                    name=clean_skill_name,
                    category="technical",
                    proficiency="intermediate",
                )
                await self.profile_repo.create_skill(new_skill)

        logger.info(f"Promoted confirmed clarification answer to candidate profile for user {user_id}: {requirement}")
        return {"status": "promoted", "requirement": requirement}

    def _formulate_question(
        self,
        category: str,
        requirement: str,
        is_mandatory: bool,
        match_status: str,
        gap_type: Optional[str],
        job_title: str,
        company_name: str,
    ) -> tuple[str, str]:
        """Formulate specific, non-repetitive, actionable clarification question and context."""
        importance = "required" if is_mandatory else "preferred"

        if match_status == "unverified":
            question = (
                f"Your profile mentions experience with '{requirement}', but it lacks supporting context or evidence. "
                f"How have you applied this in past projects or roles?"
            )
            context = (
                f"'{requirement}' is a {importance} requirement for {job_title} at {company_name}. "
                "Adding details will allow the AI CV tailor to highlight this accomplishment accurately."
            )
        elif category in ("skills", "technologies"):
            question = (
                f"The job requires '{requirement}'. Have you worked with this technology, and what did you build or achieve with it?"
            )
            context = (
                f"No verified mention of '{requirement}' was found in your profile. "
                "If you have hands-on experience, provide details here so it can be included."
            )
        elif category in ("experience", "responsibilities"):
            question = (
                f"Do you have practical experience with '{requirement}'? Please share a concrete example."
            )
            context = (
                f"This is a key {importance} responsibility for the {job_title} role at {company_name}."
            )
        elif category in ("education", "certifications"):
            question = (
                f"Do you possess or are you currently working toward '{requirement}'?"
            )
            context = f"This qualification was listed as {importance} for this opportunity."
        else:
            question = f"Could you provide context on your experience regarding '{requirement}'?"
            context = f"This requirement was identified as {importance} during job description analysis."

        return question, context


def get_clarification_service(
    session: AsyncSession = Depends(get_db_session),
) -> ClarificationService:
    job_repo = PostgresJobTargetRepository(session)
    profile_repo = PostgresProfileRepository(session)
    return ClarificationService(
        job_target_repository=job_repo,
        profile_repository=profile_repo,
    )
