import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union

from app.models.auth_session import AuthSession


class IAuthSessionRepository(ABC):
    """Abstract repository interface for AuthSession persistence operations."""

    @abstractmethod
    async def create_session(
        self,
        user_id: Union[uuid.UUID, str],
        token_hash: str,
        expires_at: datetime,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuthSession:
        """Persist a new refresh session."""
        pass

    @abstractmethod
    async def get_active_session_by_token_hash(self, token_hash: str) -> Optional[AuthSession]:
        """Look up an active (unrevoked and non-expired) session by token hash."""
        pass

    @abstractmethod
    async def get_session_by_token_hash(self, token_hash: str) -> Optional[AuthSession]:
        """Look up any session by token hash (including revoked/expired)."""
        pass

    @abstractmethod
    async def revoke_session(self, session_id: Union[uuid.UUID, str], revoked_at: Optional[datetime] = None) -> None:
        """Revoke a specific session."""
        pass

    @abstractmethod
    async def revoke_all_user_sessions(self, user_id: Union[uuid.UUID, str], revoked_at: Optional[datetime] = None) -> None:
        """Revoke all active sessions belonging to a user."""
        pass

    @abstractmethod
    async def update_last_used(self, session_id: Union[uuid.UUID, str], last_used_at: Optional[datetime] = None) -> None:
        """Update last_used_at timestamp for a session."""
        pass
