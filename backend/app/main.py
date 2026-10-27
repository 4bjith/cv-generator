from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.middleware import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
)
from app.db.session import close_db_engine, get_engine

settings = get_settings()

# Initialize structured logging subsystem
setup_logging(level=settings.log_level, log_format=settings.log_format)
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan lifecycle events."""
    logger.info(
        f"Starting {settings.app_name} [env={settings.app_env}, debug={settings.debug}]",
        extra={"event": "startup", "app_env": settings.app_env},
    )
    # Initialize engine
    engine = get_engine()
    if settings.database_url.startswith("sqlite"):
        async with engine.begin() as conn:
            from app.db.base import Base
            import app.models  # noqa: F401
            await conn.run_sync(Base.metadata.create_all)
        logger.info("SQLite database tables verified/created successfully.")

    if not settings.is_testing:
        try:
            from app.workers.scheduler import start_agent_scheduler
            start_agent_scheduler()
        except Exception as sched_exc:
            logger.warning(f"Could not start agent scheduler: {sched_exc}")

    yield

    logger.info("Shutting down AI CV Maker API", extra={"event": "shutdown"})
    if not settings.is_testing:
        try:
            from app.workers.scheduler import shutdown_agent_scheduler
            shutdown_agent_scheduler()
        except Exception as sched_exc:
            logger.warning(f"Could not shut down agent scheduler cleanly: {sched_exc}")

    try:
        from app.ai.factory import get_ai_provider
        ai_provider = get_ai_provider()
        if hasattr(ai_provider, "aclose"):
            await ai_provider.aclose()
    except Exception as exc:
        logger.warning(f"Error during AI provider cleanup: {exc}")
    await close_db_engine()


def create_app() -> FastAPI:
    """FastAPI Application Factory."""
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Evidence-backed job application assistant API.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Security Headers Middleware (outermost response modification)
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. Structured Logging Middleware
    app.add_middleware(StructuredLoggingMiddleware)

    # 3. Request ID Correlation Middleware
    app.add_middleware(RequestIDMiddleware)

    # 4. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Register centralized exception handlers
    register_exception_handlers(app)

    # Mount API routers
    app.include_router(api_router)

    return app


app = create_app()
