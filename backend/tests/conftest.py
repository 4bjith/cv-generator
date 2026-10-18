import asyncio
import os
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
import app.db.session as db_session_module

settings = get_settings()

# Primary integration test database is PostgreSQL (cv_generator_test)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    getattr(settings, "test_database_url", "postgresql+asyncpg://postgres:postgres@localhost:5432/cv_generator_test"),
)

# Apply test database URL and deterministic test configuration to settings
settings.database_url = TEST_DATABASE_URL
settings.app_env = "test"
settings.ai_provider = "mock"

from app.ai.factory import clear_ai_provider_cache
clear_ai_provider_cache()

# Create async test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False,
    future=True,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Set global engine and session factory in app.db.session
db_session_module._engine = test_engine
db_session_module._session_factory = TestingSessionLocal


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def init_test_schema():
    """Reset test database schema before running integration test suite."""
    async with test_engine.begin() as conn:
        if "postgresql" in str(test_engine.url):
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE;"))
            await conn.execute(text("CREATE SCHEMA public;"))
        await conn.run_sync(Base.metadata.create_all)



@pytest.fixture(autouse=True)
async def prepare_database():
    """Ensure tables exist and clean them after each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        if "postgresql" in str(test_engine.url):
            await conn.execute(text("TRUNCATE TABLE auth_sessions, users CASCADE;"))
        else:
            await conn.execute(text("DELETE FROM evidence_associations;"))
            await conn.execute(text("DELETE FROM evidence_items;"))
            await conn.execute(text("DELETE FROM skill_experiences;"))
            await conn.execute(text("DELETE FROM skill_projects;"))
            await conn.execute(text("DELETE FROM skill_certifications;"))
            await conn.execute(text("DELETE FROM skill_achievements;"))
            await conn.execute(text("DELETE FROM work_experiences;"))
            await conn.execute(text("DELETE FROM candidate_skills;"))
            await conn.execute(text("DELETE FROM projects;"))
            await conn.execute(text("DELETE FROM education_records;"))
            await conn.execute(text("DELETE FROM certifications;"))
            await conn.execute(text("DELETE FROM achievements;"))
            await conn.execute(text("DELETE FROM candidate_languages;"))
            await conn.execute(text("DELETE FROM candidate_links;"))
            await conn.execute(text("DELETE FROM career_preferences;"))
            await conn.execute(text("DELETE FROM candidate_profiles;"))
            await conn.execute(text("DELETE FROM auth_sessions;"))
            await conn.execute(text("DELETE FROM users;"))







async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency override yielding test database sessions."""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Apply dependency override to FastAPI app
app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a direct AsyncSession fixture for database assertion tests."""
    async with TestingSessionLocal() as session:
        yield session
