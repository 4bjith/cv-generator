from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.interfaces.auth_session_repository import IAuthSessionRepository
from app.repositories.interfaces.user_repository import IUserRepository
from app.repositories.postgres.auth_session_repository import PostgresAuthSessionRepository
from app.repositories.postgres.user_repository import PostgresUserRepository


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    """FastAPI dependency provider for IUserRepository backed by PostgreSQL / SQLAlchemy."""
    return PostgresUserRepository(session)


def get_auth_session_repository(
    session: AsyncSession = Depends(get_db_session),
) -> IAuthSessionRepository:
    """FastAPI dependency provider for IAuthSessionRepository backed by PostgreSQL / SQLAlchemy."""
    return PostgresAuthSessionRepository(session)
