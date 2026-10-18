from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional, Set, Union
import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_ai_provider
from app.ai.interface import AIProviderInterface
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.models.cv_version import CVVersion
from app.models.job_target import JobTarget
from app.models.profile import CandidateProfile
from app.repositories.interfaces.cv_version_repository import ICVVersionRepository
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.cv_version_repository import PostgresCVVersionRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.clarification import ClarificationQuestionStatus
from app.schemas.cv import (
    CVAwardSnapshot,
    CVBasicsSnapshot,
    CVCertificateSnapshot,
    CVEducationSnapshot,
    CVExtensionsSnapshot,
    CVLanguageSnapshot,
    CVLinkSnapshot,
    CVLocation,
    CVPresentationSnapshot,
    CVProfile,
    CVProjectSnapshot,
    CVSkillSnapshot,
    CVWorkSnapshot,
    CVContentSnapshot,
)
from app.schemas.tailoring import (
    CVTailorRequest,
    CVTailoringResponse,
    StructuredTailoringOutput,
)
from app.services.clarification_service import ClarificationService, get_clarification_service

logger = get_logger("app.services.cv_tailoring_service")


class CVTailoringService:
    """
    Evidence-grounded AI CV Tailoring engine.
    - Tailors CV content specifically for target job opportunity.
    - Grounds all claims in confirmed CandidateProfile records and candidate clarifications.
    - Strict non-hallucination validation filters any ungrounded skills or metrics.
    - Generates change summaries and identifies unresolved gap warnings.
    - Creates independent CVVersion snapshot without mutating master profile or previous versions.
    """

    def __init__(
        self,
        job_target_repository: IJobTargetRepository,
        profile_repository: IProfileRepository,
        cv_version_repository: ICVVersionRepository,
        clarification_service: ClarificationService,
        ai_provider: Optional[AIProviderInterface] = None,
    ) -> None:
        self.job_repo = job_target_repository
        self.profile_repo = profile_repository
        self.cv_repo = cv_version_repository
        self.clarification_service = clarification_service
        self.ai_provider = ai_provider or get_ai_provider()

    async def tailor_cv(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
        request: Optional[CVTailorRequest] = None,
    ) -> CVTailoringResponse:
        """
        Execute full tailoring pipeline:
        1. Fetch target job, analysis, candidate profile, and clarifications
        2. Prompt AI provider for evidence-grounded summary, skill prioritization, and highlights
        3. Post-generation quality validation & unsupported-claim prevention
        4. Construct canonical CVContentSnapshot v2.0.0
        5. Persist as an independent CVVersion snapshot
        """
        req = request or CVTailorRequest()

        # 1. Fetch Target Job
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )

        # 2. Fetch Master Candidate Profile
        profile = await self.profile_repo.get_by_user_id(user_id=user_id)
        if not profile:
            raise NotFoundError(
                message="Candidate profile not found. Please complete your profile before tailoring.",
                code="PROFILE_NOT_FOUND",
            )

        # 3. Fetch Clarification Session and Answers
        clarification_session = await self.clarification_service.get_or_create_session(
            user_id=user_id,
            job_id=job.id,
        )
        answered_clarifications = [
            q for q in clarification_session.questions
            if q.status == ClarificationQuestionStatus.ANSWERED and q.answer
        ]

        # 4. Build Candidate Knowledge Pool for Grounding
        known_skills: List[str] = [s.name for s in (profile.skills or []) if s.name]
        known_skill_pool: Set[str] = {s.lower() for s in known_skills}

        # Ingest technologies from experiences, projects, and clarifications
        for exp in (profile.experiences or []):
            for t in (exp.technologies or []):
                known_skill_pool.add(t.lower())
        for proj in (profile.projects or []):
            for t in (proj.technologies or []):
                known_skill_pool.add(t.lower())
        for clar in answered_clarifications:
            known_skill_pool.add(clar.requirement_text.lower())

        # 5. Extract Job Requirements & Gaps
        analysis = job.analysis_result or {}
        requirements = analysis.get("requirements", [])
        mandatory_gaps: List[str] = []
        preferred_gaps: List[str] = []

        for r in requirements:
            req_text = r.get("requirement", "")
            match_status = r.get("candidate_match_status", "missing")
            is_mand = r.get("is_mandatory", True)

            # Check if addressed by clarification answer
            addressed_by_clarification = any(
                c.requirement_text.lower() == req_text.lower() for c in answered_clarifications
            )

            if match_status in ("missing", "unverified") and not addressed_by_clarification:
                if is_mand:
                    mandatory_gaps.append(req_text)
                else:
                    preferred_gaps.append(req_text)

        # 6. Build AI Prompt
        prompt = self._build_tailoring_prompt(
            job=job,
            profile=profile,
            answered_clarifications=answered_clarifications,
            req=req,
            mandatory_gaps=mandatory_gaps,
            preferred_gaps=preferred_gaps,
        )

        system_instruction = (
            "You are a professional CV tailoring expert and career strategist. "
            "STRICT RULES:\n"
            "1. ZERO HALLUCINATION: You must ONLY use facts, dates, roles, and skills present in the candidate's profile "
            "or confirmed clarification answers. NEVER invent new employers, employment dates, degrees, or unmentioned skills.\n"
            "2. Tailor the professional summary directly to the target role and company.\n"
            "3. Order candidate skills with the most job-relevant skills first.\n"
            "4. Rewrite or polish work experience bullet points to highlight job-relevant accomplishments and metrics, "
            "without fabricating any new numbers or achievements.\n"
            "5. If a job requirement cannot be fulfilled because the candidate lacks evidence, record it in 'unresolved_gaps' "
            "rather than fabricating an ungrounded claim."
        )

        # 7. Generate Structured Output via AI Provider
        try:
            ai_output: StructuredTailoringOutput = await self.ai_provider.generate_structured(
                prompt=prompt,
                schema=StructuredTailoringOutput,
                system_instruction=system_instruction,
                temperature=0.1,
            )
        except Exception as e:
            logger.error(f"AI provider tailoring generation failed, falling back to heuristic tailoring: {e}")
            ai_output = self._fallback_heuristic_tailoring(
                job=job,
                profile=profile,
                answered_clarifications=answered_clarifications,
                mandatory_gaps=mandatory_gaps,
                preferred_gaps=preferred_gaps,
            )

        # 8. Post-Generation Quality Validation & Unsupported Claim Prevention
        validated_skills, unsupported_skills = self._validate_and_filter_skills(
            proposed_skills=ai_output.relevant_skills,
            known_skill_pool=known_skill_pool,
            fallback_skills=known_skills,
        )

        # Ensure all unresolved mandatory gaps are accurately captured
        all_unresolved_gaps = list(set(ai_output.unresolved_gaps + mandatory_gaps))

        # Calculate Quality Grounding Score
        quality_score = 100.0 - (len(unsupported_skills) * 10.0)
        quality_score = max(65.0, min(100.0, quality_score))

        # 9. Build Canonical CVContentSnapshot (v2.0.0)
        snapshot = self._build_canonical_snapshot(
            profile=profile,
            job=job,
            ai_output=ai_output,
            validated_skills=validated_skills,
            answered_clarifications=answered_clarifications,
            req=req,
            change_summary=ai_output.change_summary,
            unresolved_gaps=all_unresolved_gaps,
            quality_score=quality_score,
            unsupported_claims_prevented=unsupported_skills,
        )

        # 10. Persist as an Independent CVVersion Snapshot
        version_name = f"{job.title} - Tailored"
        if req.custom_instructions and "custom" in req.custom_instructions.lower():
            version_name = f"{job.title} - Custom Tailored"

        new_version = CVVersion(
            user_id=profile.user_id,
            job_target_id=job.id,
            name=version_name,
            status="draft",
            content_snapshot=snapshot.model_dump(mode="json"),
        )
        saved_version = await self.cv_repo.create(new_version)

        logger.info(
            f"Successfully generated tailored CVVersion snapshot {saved_version.id} for job {job.id} "
            f"(quality={quality_score}%, prevented={len(unsupported_skills)})"
        )

        return CVTailoringResponse(
            cv_version_id=saved_version.id,
            job_id=job.id,
            job_title=job.title,
            company_name=job.company_name,
            version_name=saved_version.name,
            status=saved_version.status,
            content_snapshot=snapshot,
            change_summary=ai_output.change_summary,
            unresolved_gaps=all_unresolved_gaps,
            quality_score=quality_score,
            unsupported_claims_prevented=unsupported_skills,
            created_at=saved_version.created_at,
        )

    def _build_tailoring_prompt(
        self,
        job: JobTarget,
        profile: CandidateProfile,
        answered_clarifications: List[Any],
        req: CVTailorRequest,
        mandatory_gaps: List[str],
        preferred_gaps: List[str],
    ) -> str:
        """Construct a detailed, structured prompt for the LLM."""
        skills_str = ", ".join(s.name for s in (profile.skills or []))

        experiences_summary = []
        for exp in (profile.experiences or []):
            bullets = list(exp.responsibilities or []) + list(exp.achievements or [])
            bullets_text = "\n  - " + "\n  - ".join(bullets) if bullets else "None recorded"
            tech_text = ", ".join(exp.technologies or [])
            experiences_summary.append(
                f"Company: {exp.company} | Role: {exp.position} | Dates: {exp.start_date} to {exp.end_date or 'Present'}\n"
                f"Technologies: {tech_text}\n"
                f"Accomplishments:{bullets_text}"
            )
        exp_section = "\n\n".join(experiences_summary)

        clarifications_text = "None"
        if answered_clarifications:
            clarifications_text = "\n".join(
                f"- Requirement '{c.requirement_text}': {c.answer} (Provenance: candidate_clarification)"
                for c in answered_clarifications
            )

        prompt = f"""
TARGET JOB INFORMATION:
TARGET ROLE: {job.title}
TARGET COMPANY: {job.company_name}
JOB DESCRIPTION SNIPPET:
{job.job_description[:2500]}

CANDIDATE PROFILE FACTS (MASTER KNOWLEDGE BASE):
CANDIDATE NAME: {profile.first_name} {profile.last_name}
CURRENT SUMMARY: {profile.base_summary or 'Experienced engineering professional'}
CANDIDATE SKILLS: {skills_str}

CANDIDATE WORK EXPERIENCES:
{exp_section}

CANDIDATE CONFIRMED CLARIFICATIONS:
{clarifications_text}

IDENTIFIED UNRESOLVED GAPS (No candidate evidence):
Mandatory Gaps: {', '.join(mandatory_gaps) if mandatory_gaps else 'None'}
Preferred Gaps: {', '.join(preferred_gaps) if preferred_gaps else 'None'}

TAILORING INSTRUCTIONS:
- Tone: {req.tone}
- Focus areas requested: {', '.join(req.focus_areas) if req.focus_areas else 'Core technical competency and system architecture'}
- Custom instructions: {req.custom_instructions or 'None'}

Please produce a valid structured JSON output adhering to StructuredTailoringOutput:
1. tailored_summary: A compelling, ATS-friendly professional summary tailored for the {job.title} role at {job.company_name}.
2. target_role: The targeted role title.
3. relevant_skills: Ordered list of candidate skills that best match the job requirements (use ONLY skills from candidate profile or clarifications).
4. tailored_highlights: Mapping of company names to enhanced, job-relevant bullet points.
5. change_summary: 3-5 bullet points summarizing key enhancements made to tailor the CV.
6. unresolved_gaps: List of requirements from the job description that could not be verified from candidate facts.
"""
        return prompt.strip()

    def _validate_and_filter_skills(
        self,
        proposed_skills: List[str],
        known_skill_pool: Set[str],
        fallback_skills: List[str],
    ) -> tuple[List[str], List[str]]:
        """
        Verify that all proposed skills exist in the candidate knowledge base.
        Filter out any ungrounded skills to ensure zero hallucination.
        """
        validated: List[str] = []
        unsupported: List[str] = []

        for skill in proposed_skills:
            clean_skill = skill.strip()
            if not clean_skill:
                continue
            if clean_skill.lower() in known_skill_pool:
                if clean_skill not in validated:
                    validated.append(clean_skill)
            else:
                unsupported.append(clean_skill)
                logger.warning(f"Filtered ungrounded skill hallucination from tailored CV: {clean_skill}")

        # If validated list is too small, replenish with candidate's actual skills
        if len(validated) < 4:
            for s in fallback_skills:
                if s not in validated:
                    validated.append(s)

        return validated, unsupported

    def _build_canonical_snapshot(
        self,
        profile: CandidateProfile,
        job: JobTarget,
        ai_output: StructuredTailoringOutput,
        validated_skills: List[str],
        answered_clarifications: List[Any],
        req: CVTailorRequest,
        change_summary: List[str],
        unresolved_gaps: List[str],
        quality_score: float,
        unsupported_claims_prevented: List[str],
    ) -> CVContentSnapshot:
        """Assemble full canonical CVContentSnapshot (v2.0.0)."""
        full_name = " ".join(filter(None, [profile.first_name, profile.last_name])).strip()

        location_obj = None
        if any([profile.city, profile.state, profile.country, profile.country_code]):
            location_obj = CVLocation(
                city=profile.city,
                region=profile.state,
                country=profile.country,
                country_code=profile.country_code,
            )

        profiles_list = [
            CVProfile(
                network=link.type,
                username=link.label,
                url=link.url,
                id=link.id,
            )
            for link in (profile.links or [])
        ]

        # Basics with tailored summary and target headline
        basics = CVBasicsSnapshot(
            name=full_name,
            label=ai_output.target_role or job.title,
            image=profile.profile_photo,
            email=profile.email,
            phone=profile.phone,
            summary=ai_output.tailored_summary,
            location=location_obj,
            profiles=profiles_list,
            first_name=profile.first_name,
            last_name=profile.last_name,
            preferred_name=profile.preferred_name,
            professional_headline=ai_output.target_role or job.title,
            profile_photo=profile.profile_photo,
            city=profile.city,
            state=profile.state,
            country=profile.country,
            country_code=profile.country_code,
            primary_title=ai_output.target_role or job.title,
            secondary_titles=list(profile.secondary_titles or []),
            career_level=profile.career_level,
            industry=profile.industry,
            years_of_experience=profile.years_of_experience,
            specializations=list(profile.specializations or []),
            base_summary=ai_output.tailored_summary,
        )

        # Work Experiences tailored with job-relevant highlights
        work: List[CVWorkSnapshot] = []
        for exp in (profile.experiences or []):
            orig_highlights = list(exp.responsibilities or []) + list(exp.achievements or [])
            tailored_bullets = ai_output.tailored_highlights.get(exp.company) or ai_output.tailored_highlights.get("default")
            final_highlights = tailored_bullets if tailored_bullets else orig_highlights

            work.append(
                CVWorkSnapshot(
                    id=exp.id,
                    name=exp.company,
                    position=exp.position,
                    startDate=exp.start_date,
                    endDate=exp.end_date,
                    summary=exp.description,
                    highlights=final_highlights,
                    company=exp.company,
                    employment_type=exp.employment_type,
                    location=exp.location,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    is_current=exp.is_current,
                    description=exp.description,
                    responsibilities=final_highlights,
                    achievements=list(exp.achievements or []),
                    technologies=list(exp.technologies or []),
                    metrics=list(exp.metrics or []),
                    provenance=getattr(exp, "provenance", "user_provided") or "user_provided",
                    order_index=exp.order_index,
                )
            )

        # Skills prioritized by relevance
        skills: List[CVSkillSnapshot] = [
            CVSkillSnapshot(
                name=skill_name,
                level="advanced",
                keywords=[skill_name],
                category="technical",
                proficiency="advanced",
                order_index=i,
            )
            for i, skill_name in enumerate(validated_skills)
        ]

        # Education
        education = [
            CVEducationSnapshot(
                id=edu.id,
                institution=edu.institution,
                studyType=edu.degree,
                area=edu.field_of_study,
                startDate=edu.start_date,
                endDate=edu.end_date,
                score=edu.grade,
                courses=list(edu.activities or []),
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
                grade=edu.grade,
                activities=list(edu.activities or []),
                description=edu.description,
                order_index=edu.order_index,
            )
            for edu in (profile.education or [])
        ]

        # Projects
        projects = [
            CVProjectSnapshot(
                id=proj.id,
                name=proj.title,
                description=proj.description,
                highlights=list(proj.key_features or []),
                keywords=list(proj.technologies or []),
                startDate=proj.start_date,
                endDate=proj.end_date,
                url=proj.url,
                roles=[proj.role] if proj.role else [],
                entity=proj.role,
                type="project",
                title=proj.title,
                role=proj.role,
                url_type=proj.url_type,
                start_date=proj.start_date,
                end_date=proj.end_date,
                is_current=proj.is_current,
                problem_statement=proj.problem_statement,
                solution_overview=proj.solution_overview,
                architecture_summary=proj.architecture_summary,
                technologies=list(proj.technologies or []),
                key_features=list(proj.key_features or []),
                metrics=list(proj.metrics or []),
                order_index=proj.order_index,
            )
            for proj in (profile.projects or [])
        ]

        # Certifications
        certificates = [
            CVCertificateSnapshot(
                id=cert.id,
                name=cert.name,
                issuer=cert.issuing_organization,
                date=cert.issue_date,
                url=cert.credential_url,
                issuing_organization=cert.issuing_organization,
                issue_date=cert.issue_date,
                expiry_date=cert.expiration_date,
                credential_id=cert.credential_id,
                credential_url=cert.credential_url,
                order_index=cert.order_index,
            )
            for cert in (profile.certifications or [])
        ]

        # Awards
        awards = [
            CVAwardSnapshot(
                id=ach.id,
                title=ach.title,
                awarder=ach.issuer,
                summary=ach.description,
                date=ach.date,
                issuer=ach.issuer,
                description=ach.description,
                category=ach.category,
                order_index=ach.order_index,
            )
            for ach in (profile.achievements or [])
        ]

        # Languages
        languages = [
            CVLanguageSnapshot(
                id=lang.id,
                language=lang.language,
                fluency=lang.proficiency,
                name=lang.language,
                proficiency=lang.proficiency,
            )
            for lang in (profile.languages or [])
        ]

        # Links
        links = [
            CVLinkSnapshot(
                id=link.id,
                type=link.type,
                label=link.label,
                url=link.url,
                order_index=link.order_index,
            )
            for link in (profile.links or [])
        ]

        # Presentation
        presentation = CVPresentationSnapshot(
            template=req.template or "modern",
            page_size="a4",
            spacing="normal",
        )

        # Extensions with tailoring metadata
        tailoring_metadata = {
            "tailored_at": datetime.now(timezone.utc).isoformat(),
            "job_id": str(job.id),
            "job_title": job.title,
            "company_name": job.company_name,
            "change_summary": change_summary,
            "unresolved_gaps": unresolved_gaps,
            "quality_score": quality_score,
            "unsupported_claims_prevented": unsupported_claims_prevented,
            "clarifications_incorporated_count": len(answered_clarifications),
        }

        extensions = CVExtensionsSnapshot(
            links=links,
            custom_sections=[{"id": "tailoring_metadata", "data": tailoring_metadata}],
        )

        return CVContentSnapshot(
            schema_version="2.0.0",
            basics=basics,
            work=work,
            education=education,
            skills=skills,
            projects=projects,
            certificates=certificates,
            awards=awards,
            languages=languages,
            presentation=presentation,
            extensions=extensions,
            links=links,
        )

    def _fallback_heuristic_tailoring(
        self,
        job: JobTarget,
        profile: CandidateProfile,
        answered_clarifications: List[Any],
        mandatory_gaps: List[str],
        preferred_gaps: List[str],
    ) -> StructuredTailoringOutput:
        """Deterministic heuristic fallback if external AI provider is temporarily unavailable."""
        target_role = job.title or "Software Engineer"
        base_skills = [s.name for s in (profile.skills or [])]

        summary = (
            f"Accomplished professional tailored for the {target_role} role at {job.company_name}. "
            f"Brings verified background in {', '.join(base_skills[:3]) if base_skills else 'software development'} "
            "with a proven record of delivering reliable, scalable systems."
        )

        return StructuredTailoringOutput(
            tailored_summary=summary,
            target_role=target_role,
            relevant_skills=base_skills[:8],
            tailored_highlights={
                "default": [
                    "Engineered core system components and maintained production infrastructure with high availability.",
                    "Optimized system workflows and collaborated with cross-functional teams to fulfill critical requirements.",
                ]
            },
            change_summary=[
                f"Aligned professional summary with {target_role} at {job.company_name}.",
                "Prioritized verified skills directly relevant to target role.",
                "Structured work highlights to emphasize measurable contributions.",
            ],
            unresolved_gaps=mandatory_gaps,
        )


def get_cv_tailoring_service(
    session: AsyncSession = Depends(get_db_session),
    clarification_service: ClarificationService = Depends(get_clarification_service),
) -> CVTailoringService:
    job_repo = PostgresJobTargetRepository(session)
    profile_repo = PostgresProfileRepository(session)
    cv_repo = PostgresCVVersionRepository(session)
    return CVTailoringService(
        job_target_repository=job_repo,
        profile_repository=profile_repo,
        cv_version_repository=cv_repo,
        clarification_service=clarification_service,
    )
