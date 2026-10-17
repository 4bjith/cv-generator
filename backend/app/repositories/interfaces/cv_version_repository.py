import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from app.models.cv_version import CVVersion


class ICVVersionRepository(ABC):
    """Abstract repository interface for CV Version persistence operations."""

    @abstractmethod
    async def create(self, cv_version: CVVersion) -> CVVersion:
        """Persist a new CV version."""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        version_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[CVVersion]:
        """Retrieve a specific CV version owned by user_id."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        job_target_id: Optional[Union[uuid.UUID, str]] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[CVVersion], int]:
        """List CV versions owned by user_id with optional filters and pagination."""
        pass

    @abstractmethod
    async def update(self, cv_version: CVVersion) -> CVVersion:
        """Update an existing CV version."""
        pass

    @abstractmethod
    async def delete(self, cv_version: CVVersion) -> None:
        """Delete a CV version."""
        pass
