import uuid
from datetime import datetime
from typing import Optional, Union
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utc_now
from app.models.auth_session import AuthSession
from app.repositories.interfaces.auth_session_repository import IAuthSessionRepository


class PostgresAuthSessionRepository(IAuthSessionRepository):
    """PostgreSQL / SQLAlchemy implementation of IAuthSessionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self,
        user_id: Union[uuid.UUID, str],
        token_hash: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuthSession:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        now = utc_now()
        auth_session = AuthSession(
            id=uuid.uuid4(),
            user_id=user_id,
            refresh_token_hash=token_hash,
            expires_at=expires_at,
            revoked_at=None,
            created_at=now,
            last_used_at=now,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.session.add(auth_session)
        await self.session.flush()
        return auth_session

    async def get_active_session_by_token_hash(self, token_hash: str) -> Optional[AuthSession]:
        now = utc_now()
        result = await self.session.execute(
            select(AuthSession).where(
                AuthSession.refresh_token_hash == token_hash,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > now,
            )
        )
        return result.scalars().first()

    async def get_session_by_token_hash(self, token_hash: str) -> Optional[AuthSession]:
        result = await self.session.execute(
            select(AuthSession).where(AuthSession.refresh_token_hash == token_hash)
        )
        return result.scalars().first()

    async def revoke_session(
        self,
        session_id: Union[uuid.UUID, str],
        revoked_at: Optional[datetime] = None,
    ) -> None:
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)

        revoke_time = revoked_at or utc_now()
        await self.session.execute(
            update(AuthSession)
            .where(AuthSession.id == session_id)
            .values(revoked_at=revoke_time)
        )
        await self.session.flush()

    async def revoke_all_user_sessions(
        self,
        user_id: Union[uuid.UUID, str],
        revoked_at: Optional[datetime] = None,
    ) -> None:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        revoke_time = revoked_at or utc_now()
        await self.session.execute(
            update(AuthSession)
            .where(
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=revoke_time)
        )
        await self.session.flush()

    async def update_last_used(
        self,
        session_id: Union[uuid.UUID, str],
        last_used_at: Optional[datetime] = None,
    ) -> None:
        if isinstance(session_id, str):
            session_id = uuid.UUID(session_id)

        used_time = last_used_at or utc_now()
        await self.session.execute(
            update(AuthSession)
            .where(AuthSession.id == session_id)
            .values(last_used_at=used_time)
        )
        await self.session.flush()
