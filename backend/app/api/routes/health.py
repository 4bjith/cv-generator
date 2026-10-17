from fastapi import APIRouter, Response, status
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
    description="Comprehensive readiness check assessing whether the application and database can safely handle traffic.",
)
async def readiness_check(response: Response) -> HealthReadyResponse:
    """Return readiness state, actively validating database connectivity."""
    db_ok = await check_database_health()

    checks = {
        "application": "ok",
        "database": "ok" if db_ok else "unavailable",
    }

    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthReadyResponse(status="degraded", checks=checks)

    return HealthReadyResponse(status="ok", checks=checks)


# Legacy endpoint support
legacy_router = APIRouter(tags=["health"])


@legacy_router.get(
    "/health",
    summary="Legacy Health Check",
    description="Backward-compatible health endpoint for legacy tooling.",
)
async def legacy_health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ai-cv-maker-backend"}
