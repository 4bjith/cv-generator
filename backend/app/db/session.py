from typing import AsyncGenerator, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("app.db")
settings = get_settings()

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine(database_url: Optional[str] = None) -> AsyncEngine:
    """Return the global AsyncEngine instance, initializing it if needed."""
    global _engine
    if _engine is not None and database_url is None:
        return _engine

    url = database_url or settings.database_url

    # Check if using SQLite (useful for automated tests)
    is_sqlite = url.startswith("sqlite")

    engine_kwargs: dict = {
        "echo": settings.db_echo,
        "future": True,
    }

    if not is_sqlite:
        engine_kwargs.update({
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": settings.db_pool_timeout,
            "pool_recycle": settings.db_pool_recycle,
            "pool_pre_ping": True,
        })
    else:
        # SQLite in-memory or file testing
        engine_kwargs.update({
            "poolclass": NullPool,
        })

    engine = create_async_engine(url, **engine_kwargs)

    if database_url is None:
        _engine = engine

    return engine


def get_session_factory(database_url: Optional[str] = None) -> async_sessionmaker[AsyncSession]:
    """Return the global sessionmaker factory."""
    global _session_factory
    if _session_factory is not None and database_url is None:
        return _session_factory

    engine = get_engine(database_url)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    if database_url is None:
        _session_factory = factory

    return factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped AsyncSession."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> bool:
    """Execute a lightweight query to determine whether the database is responsive."""
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as exc:
        logger.warning(f"Database health check failed: {str(exc)}")
        return False


async def close_db_engine() -> None:
    """Dispose the engine and close all connections in the connection pool."""
    global _engine, _session_factory
    if _engine is not None:
        logger.info("Disposing database connection pool.")
        await _engine.dispose()
        _engine = None
        _session_factory = None
