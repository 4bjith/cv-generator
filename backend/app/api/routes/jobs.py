from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.schemas.auth import UserResponse
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
from app.services.cv_service import CVService, get_cv_service
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
