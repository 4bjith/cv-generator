import uuid
from datetime import datetime
from typing import Optional, Union
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.interfaces.user_repository import IUserRepository


class PostgresUserRepository(IUserRepository):
    """PostgreSQL / SQLAlchemy implementation of IUserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: Union[uuid.UUID, str]) -> Optional[User]:
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        normalized_email = email.strip().lower()
        result = await self.session.execute(
            select(User).where(User.email == normalized_email)
        )
        return result.scalars().first()

    async def create(self, email: str, password_hash: str, name: str) -> User:
        normalized_email = email.strip().lower()
        user = User(
            id=uuid.uuid4(),
            email=normalized_email,
            password_hash=password_hash,
            name=name.strip(),
            is_active=True,
            is_verified=False,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_last_login(self, user_id: Union[uuid.UUID, str], login_time: datetime) -> None:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        await self.session.execute(
            update(User).where(User.id == user_id).values(last_login_at=login_time)
        )
        await self.session.flush()
