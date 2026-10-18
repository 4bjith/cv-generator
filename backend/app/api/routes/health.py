from fastapi import APIRouter, Response, status
from app.core.config import get_settings
from app.db.session import check_database_health
from app.schemas.common import HealthLiveResponse, HealthReadyResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/live",
    response_model=HealthLiveResponse,
    summary="Liveness Probe",
    description="Lightweight endpoint indicating whether the application process is alive. Does not probe database.",
)
async def liveness_check() -> HealthLiveResponse:
    """Return process liveness confirmation for container orchestrators and load balancers."""
    return HealthLiveResponse(status="ok")


@router.get(
    "/ready",
    response_model=HealthReadyResponse,
    summary="Readiness Probe",
    description="Comprehensive readiness check assessing whether the application, database, and AI dependencies are ready.",
)
async def readiness_check(response: Response) -> HealthReadyResponse:
    """Return readiness state, actively validating database connectivity and safe AI metadata."""
    db_ok = await check_database_health()
    settings = get_settings()

    checks = {
        "application": "ok",
        "database": "ok" if db_ok else "unavailable",
    }

    # Safe AI metadata (Never return credentials, secret fragments, or raw provider exceptions)
    ai_metadata = {
        "provider": settings.ai_provider,
        "model": settings.gemini_model,
        "embedding_model": settings.gemini_embedding_model,
        "configured": bool(settings.gemini_api_key and settings.gemini_api_key.strip()),
    }

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthReadyResponse(status="degraded", checks=checks, ai=ai_metadata)

    return HealthReadyResponse(status="ok", checks=checks, ai=ai_metadata)


# Legacy endpoint support
legacy_router = APIRouter(tags=["health"])


@legacy_router.get(
    "/health",
    summary="Legacy Health Check",
    description="Backward-compatible health endpoint for legacy tooling.",
)
async def legacy_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-cv-maker-backend"}
