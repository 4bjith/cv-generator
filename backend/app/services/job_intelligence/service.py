from typing import Optional, Union
import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.models.profile import CandidateProfile
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.interfaces.profile_repository import IProfileRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.job_target import (
    JobAnalysisResponse,
    JobAnalysisResult,
    JobExtractionRequest,
    JobExtractionResult,
)
from app.services.job_intelligence.extractor import RuleBasedJobExtractor
from app.services.job_intelligence.extractor_interface import IJobExtractor
from app.services.job_intelligence.matcher import EvidenceGroundedMatcher

logger = get_logger("app.services.job_intelligence.service")


class JobIntelligenceService:
    """
    Core service coordinating job description intelligence:
    - Structured requirement extraction (skills, tools, seniority, constraints, responsibilities)
    - Evidence-grounded candidate matching against profile facts
    - Non-hallucinatory evidence traceability
    - Persistence on target job without modifying master CandidateProfile or CV versions.
    """

    def __init__(
        self,
        job_target_repository: IJobTargetRepository,
        profile_repository: IProfileRepository,
        extractor: Optional[IJobExtractor] = None,
        matcher: Optional[EvidenceGroundedMatcher] = None,
    ) -> None:
        self.job_repo = job_target_repository
        self.profile_repo = profile_repository
        self.extractor = extractor or RuleBasedJobExtractor()
        self.matcher = matcher or EvidenceGroundedMatcher()

    async def analyze_job(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> JobAnalysisResponse:
        """
        Run requirement extraction and evidence-grounded matching for a saved job target.
        Persists the structured analysis result onto the JobTarget record.
        """
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )

        # Retrieve candidate profile for evidence matching
        profile = await self.profile_repo.get_by_user_id(user_id=user_id)
        if not profile:
            # Create a detached dummy profile in memory to allow matching without failing
            uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
            profile = CandidateProfile(
                user_id=uid,
                first_name="Candidate",
                last_name="",
            )

        # 1. Structured Requirement Extraction
        extraction = await self.extractor.extract(
            text=job.job_description,
            title=job.title,
            company=job.company_name,
        )

        # 2. Evidence-Grounded Matching
        analysis = self.matcher.match(
            job_id=job.id,
            extraction=extraction,
            profile=profile,
        )

        # If job has no employment type and extraction detected one, update it
        if not job.employment_type and extraction.employment_type:
            job.employment_type = extraction.employment_type

        # 3. Persist Analysis Result on Job Target
        job.analysis_result = analysis.model_dump(mode="json")
        updated_job = await self.job_repo.update(job)

        logger.info(
            f"Analyzed job target {job.id} for user {user_id}: "
            f"{analysis.keyword_summary.supported_count}/{analysis.keyword_summary.total_requirements} supported requirements "
            f"({analysis.keyword_summary.coverage_percentage}% coverage)."
        )

        return JobAnalysisResponse(
            job_id=updated_job.id,
            job_title=updated_job.title,
            company_name=updated_job.company_name,
            analysis=analysis,
        )

    async def get_job_analysis(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> JobAnalysisResponse:
        """Retrieve existing analysis result for a job target, or run analysis if not yet performed."""
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )

        if job.analysis_result:
            try:
                analysis = JobAnalysisResult.model_validate(job.analysis_result)
                return JobAnalysisResponse(
                    job_id=job.id,
                    job_title=job.title,
                    company_name=job.company_name,
                    analysis=analysis,
                )
            except Exception as e:
                logger.warning(f"Corrupted or outdated analysis_result on job {job.id}, re-running analysis: {e}")

        # If analysis not yet performed or revalidation needed, run analyze_job
        return await self.analyze_job(user_id=user_id, job_id=job_id)

    async def extract_adhoc(
        self,
        request: JobExtractionRequest,
    ) -> JobExtractionResult:
        """Run ad-hoc requirement extraction from raw text without saving a JobTarget."""
        return await self.extractor.extract(
            text=request.job_description,
            title=request.title,
            company=request.company_name,
        )


def get_job_intelligence_service(session: AsyncSession = Depends(get_db_session)) -> JobIntelligenceService:
    """FastAPI dependency injecting JobIntelligenceService initialized with Postgres repositories."""
    job_repo = PostgresJobTargetRepository(session)
    profile_repo = PostgresProfileRepository(session)
    return JobIntelligenceService(job_repo, profile_repo)
