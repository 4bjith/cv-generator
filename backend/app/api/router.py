from fastapi import APIRouter

from app.api.routes.ats import router as ats_router
from app.api.routes.auth import router as auth_router
from app.api.routes.cover_letters import router as cover_letters_router
from app.api.routes.cv import router as cv_router
from app.api.routes.health import legacy_router as legacy_health_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.profile import router as profile_router

# Version 1 API Sub-router
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(health_router)
v1_router.include_router(auth_router)
v1_router.include_router(profile_router)
v1_router.include_router(jobs_router)
v1_router.include_router(cv_router)
v1_router.include_router(ats_router)
v1_router.include_router(cover_letters_router, prefix="/cover-letters", tags=["Cover Letters"])

# Main Application API Router
api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)

# Mount legacy routes directly under /api for backward compatibility
api_router.include_router(legacy_health_router)
