from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.schemas.ats import (
    ApplyATSSuggestionsRequest,
    ApplyATSSuggestionsResponse,
    ATSAnalysisRequest,
    ATSAnalysisResponse,
)
from app.schemas.auth import UserResponse
from app.services.ats_service import ATSService, get_ats_service

router = APIRouter(prefix="/ats", tags=["ATS Analysis & Keyword Optimization"])


@router.post(
    "/analyze",
    response_model=ATSAnalysisResponse,
    summary="Run ATS compatibility & keyword density analysis",
    description="Analyze a CV version against an optional JobTarget or general ATS parsing baseline.",
)
async def analyze_cv_ats(
    data: ATSAnalysisRequest,
    current_user: UserResponse = Depends(get_current_user),
    ats_service: ATSService = Depends(get_ats_service),
) -> ATSAnalysisResponse:
    return await ats_service.analyze_cv_version(
        user_id=current_user.id,
        cv_version_id=data.cv_version_id,
        job_id=data.job_id,
    )


@router.get(
    "/cv/{cv_version_id}",
    response_model=ATSAnalysisResponse,
    summary="Get ATS analysis for a CV version",
    description="Retrieve explainable ATS analysis and parsing friction audit for a specified CV version.",
)
async def get_cv_ats_analysis(
    cv_version_id: uuid.UUID,
    job_id: Optional[uuid.UUID] = Query(None, description="Optional target JobTarget UUID"),
    current_user: UserResponse = Depends(get_current_user),
    ats_service: ATSService = Depends(get_ats_service),
) -> ATSAnalysisResponse:
    return await ats_service.analyze_cv_version(
        user_id=current_user.id,
        cv_version_id=cv_version_id,
        job_id=job_id,
    )


@router.post(
    "/apply-suggestions",
    response_model=ApplyATSSuggestionsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply accepted grounded keyword optimizations",
    description="Create a new independent CVVersion snapshot incorporating candidate-grounded keyword improvements.",
)
async def apply_ats_suggestions(
    data: ApplyATSSuggestionsRequest,
    current_user: UserResponse = Depends(get_current_user),
    ats_service: ATSService = Depends(get_ats_service),
) -> ApplyATSSuggestionsResponse:
    return await ats_service.apply_suggestions(
        user_id=current_user.id,
        data=data,
    )
