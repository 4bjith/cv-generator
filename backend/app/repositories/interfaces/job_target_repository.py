import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from app.models.job_target import JobTarget


class IJobTargetRepository(ABC):
    """Abstract repository interface for Job Target persistence operations."""

    @abstractmethod
    async def create(self, job_target: JobTarget) -> JobTarget:
        """Persist a new job target."""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        job_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[JobTarget]:
        """Retrieve a specific job target owned by user_id."""
        pass

    @abstractmethod
    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[JobTarget], int]:
        """List job targets owned by user_id with optional status/search filters and pagination."""
        pass

    @abstractmethod
    async def update(self, job_target: JobTarget) -> JobTarget:
        """Update an existing job target."""
        pass

    @abstractmethod
    async def delete(self, job_target: JobTarget) -> None:
        """Delete a job target."""
        pass
