from typing import Any, Dict, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.clarification import (
    ClarificationAnswerRequest,
    ClarificationBulkAnswerRequest,
    ClarificationPromoteRequest,
    ClarificationSessionResponse,
)
from app.schemas.cv import CVVersionListResponse
from app.schemas.job_target import (
    JobAnalysisResponse,
    JobExtractionRequest,
    JobExtractionResult,
    JobTargetCreate,
    JobTargetListResponse,
    JobTargetResponse,
    JobTargetStatus,
    JobTargetUpdate,
)
from app.schemas.tailoring import CVTailorRequest, CVTailoringResponse
from app.services.clarification_service import ClarificationService, get_clarification_service
from app.services.cv_service import CVService, get_cv_service
from app.services.cv_tailoring_service import CVTailoringService, get_cv_tailoring_service
from app.services.job_intelligence import JobIntelligenceService, get_job_intelligence_service
from app.services.job_target_service import JobTargetService, get_job_target_service

router = APIRouter(prefix="/jobs", tags=["Job Targets"])


@router.get(
    "",
    response_model=JobTargetListResponse,
    summary="List job targets",
    description="Retrieve paginated list of job targets owned by the authenticated user, with optional search and status filtering.",
)
async def list_jobs(
    status: Optional[JobTargetStatus] = Query(None, description="Filter by status ('saved', 'archived')"),
    search: Optional[str] = Query(None, description="Search query matching title, company, or location"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: UserResponse = Depends(get_current_user),
    service: JobTargetService = Depends(get_job_target_service),
) -> JobTargetListResponse:
    status_str = status.value if status else None
    return await service.list_job_targets(
        user_id=current_user.id,
        status=status_str,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=JobTargetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job target",
    description="Create and save a new job target opportunity for the authenticated user.",
)
async def create_job(
    data: JobTargetCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: JobTargetService = Depends(get_job_target_service),
) -> JobTargetResponse:
    return await service.create_job_target(current_user.id, data)


@router.post(
    "/extract",
    response_model=JobExtractionResult,
    summary="Extract requirements ad-hoc",
    description="Extract structured requirements, seniority, and keywords from job description text without saving a JobTarget.",
)
async def extract_job_requirements(
    data: JobExtractionRequest,
    current_user: UserResponse = Depends(get_current_user),
    intelligence_service: JobIntelligenceService = Depends(get_job_intelligence_service),
) -> JobExtractionResult:
    return await intelligence_service.extract_adhoc(data)


@router.get(
    "/{job_id}",
    response_model=JobTargetResponse,
    summary="Get job target",
    description="Retrieve details of a single job target owned by the authenticated user.",
)
async def get_job(
    job_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: JobTargetService = Depends(get_job_target_service),
) -> JobTargetResponse:
    return await service.get_job_target(current_user.id, job_id)


@router.patch(
    "/{job_id}",
    response_model=JobTargetResponse,
    summary="Update job target",
    description="Update permitted fields of an existing job target.",
)
async def update_job(
    job_id: uuid.UUID,
    data: JobTargetUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: JobTargetService = Depends(get_job_target_service),
) -> JobTargetResponse:
    return await service.update_job_target(current_user.id, job_id, data)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job target",
    description="Delete a job target owned by the authenticated user.",
)
async def delete_job(
    job_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: JobTargetService = Depends(get_job_target_service),
) -> None:
    await service.delete_job_target(current_user.id, job_id)


@router.post(
    "/{job_id}/analyze",
    response_model=JobAnalysisResponse,
    summary="Analyze job target",
    description="Extract structured requirements and perform evidence-grounded candidate matching against the user's CandidateProfile.",
)
async def analyze_job(
    job_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    intelligence_service: JobIntelligenceService = Depends(get_job_intelligence_service),
) -> JobAnalysisResponse:
    return await intelligence_service.analyze_job(
        user_id=current_user.id,
        job_id=job_id,
    )


@router.get(
    "/{job_id}/analysis",
    response_model=JobAnalysisResponse,
    summary="Get job analysis",
    description="Retrieve existing evidence-grounded requirements analysis for a saved job target.",
)
async def get_job_analysis(
    job_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    intelligence_service: JobIntelligenceService = Depends(get_job_intelligence_service),
) -> JobAnalysisResponse:
    return await intelligence_service.get_job_analysis(
        user_id=current_user.id,
        job_id=job_id,
    )


@router.get(
    "/{job_id}/versions",
    response_model=CVVersionListResponse,
    summary="List CV versions for job target",
    description="List all CV versions associated with this specific job target.",
)
async def list_job_cv_versions(
    job_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    cv_service: CVService = Depends(get_cv_service),
) -> CVVersionListResponse:
    return await cv_service.list_versions(
        user_id=current_user.id,
        job_target_id=job_id,
        limit=limit,
        offset=offset,
    )


# =========================================================================
# Clarification Engine Endpoints
# =========================================================================

@router.get(
    "/{job_id}/clarifications",
    response_model=ClarificationSessionResponse,
    summary="Get or initialize clarification session",
    description="Retrieve the prioritized clarification session for this job target, or generate one if not yet initialized.",
)
async def get_clarifications(
    job_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    clarification_service: ClarificationService = Depends(get_clarification_service),
) -> ClarificationSessionResponse:
    return await clarification_service.get_or_create_session(
        user_id=current_user.id,
        job_id=job_id,
    )


@router.post(
    "/{job_id}/clarifications/{question_id}/answer",
    response_model=ClarificationSessionResponse,
    summary="Answer clarification question",
    description="Submit or update the candidate answer for a specific clarification question.",
)
async def answer_clarification_question(
    job_id: uuid.UUID,
    question_id: str,
    data: ClarificationAnswerRequest,
    current_user: UserResponse = Depends(get_current_user),
    clarification_service: ClarificationService = Depends(get_clarification_service),
) -> ClarificationSessionResponse:
    return await clarification_service.answer_question(
        user_id=current_user.id,
        job_id=job_id,
        question_id=question_id,
        data=data,
    )


@router.post(
    "/{job_id}/clarifications/{question_id}/skip",
    response_model=ClarificationSessionResponse,
    summary="Skip clarification question",
    description="Mark a clarification question as skipped for this job target.",
)
async def skip_clarification_question(
    job_id: uuid.UUID,
    question_id: str,
    current_user: UserResponse = Depends(get_current_user),
    clarification_service: ClarificationService = Depends(get_clarification_service),
) -> ClarificationSessionResponse:
    return await clarification_service.skip_question(
        user_id=current_user.id,
        job_id=job_id,
        question_id=question_id,
    )


@router.post(
    "/{job_id}/clarifications/{question_id}/promote",
    response_model=Dict[str, Any],
    summary="Promote clarification answer to candidate profile",
    description="Explicit candidate confirmation to persist an answered clarification question into the master candidate knowledge base.",
)
async def promote_clarification_answer(
    job_id: uuid.UUID,
    question_id: str,
    data: ClarificationPromoteRequest,
    current_user: UserResponse = Depends(get_current_user),
    clarification_service: ClarificationService = Depends(get_clarification_service),
) -> Dict[str, Any]:
    return await clarification_service.promote_answer_to_profile(
        user_id=current_user.id,
        job_id=job_id,
        question_id=question_id,
        data=data,
    )


@router.post(
    "/{job_id}/clarifications/bulk",
    response_model=ClarificationSessionResponse,
    summary="Bulk submit clarification answers",
    description="Submit answers to multiple clarification questions at once.",
)
async def bulk_answer_clarifications(
    job_id: uuid.UUID,
    data: ClarificationBulkAnswerRequest,
    current_user: UserResponse = Depends(get_current_user),
    clarification_service: ClarificationService = Depends(get_clarification_service),
) -> ClarificationSessionResponse:
    return await clarification_service.bulk_answer(
        user_id=current_user.id,
        job_id=job_id,
        data=data,
    )


# =========================================================================
# Evidence-Grounded AI CV Tailoring Endpoints
# =========================================================================

@router.post(
    "/{job_id}/tailor-cv",
    response_model=CVTailoringResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tailor CV with AI and evidence grounding",
    description="Generate a job-specific CV version using candidate profile facts, confirmed clarifications, and zero-hallucination verification.",
)
async def tailor_cv(
    job_id: uuid.UUID,
    data: Optional[CVTailorRequest] = None,
    current_user: UserResponse = Depends(get_current_user),
    tailoring_service: CVTailoringService = Depends(get_cv_tailoring_service),
) -> CVTailoringResponse:
    return await tailoring_service.tailor_cv(
        user_id=current_user.id,
        job_id=job_id,
        request=data,
    )


@router.post(
    "/{job_id}/cv/generate",
    response_model=CVTailoringResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate tailored CV (FRD specification alias)",
    description="Alias endpoint matching the canonical FRD specification POST /api/jobs/:id/cv/generate.",
)
async def generate_cv_for_job(
    job_id: uuid.UUID,
    data: Optional[CVTailorRequest] = None,
    current_user: UserResponse = Depends(get_current_user),
    tailoring_service: CVTailoringService = Depends(get_cv_tailoring_service),
) -> CVTailoringResponse:
    return await tailoring_service.tailor_cv(
        user_id=current_user.id,
        job_id=job_id,
        request=data,
    )
