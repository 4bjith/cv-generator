import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union

from app.models.user import User


class IUserRepository(ABC):
    """Abstract repository interface for User persistence operations."""

    @abstractmethod
    async def get_by_id(self, user_id: Union[uuid.UUID, str]) -> Optional[User]:
        """Retrieve user record by primary key UUID or string representation."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user record by unique normalized email."""
        pass

    @abstractmethod
    async def create(self, email: str, password_hash: str, name: str) -> User:
        """Create and persist a new user record."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user record."""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: Union[uuid.UUID, str], login_time: datetime) -> None:
        """Update the last_login_at timestamp for a user."""
        pass
