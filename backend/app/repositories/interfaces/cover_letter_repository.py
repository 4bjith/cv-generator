import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from app.models.cover_letter import CoverLetter


class ICoverLetterRepository(ABC):
    """Abstract repository interface for CoverLetter persistence."""

    @abstractmethod
    async def create(self, cover_letter: CoverLetter) -> CoverLetter:
        """Persist a new cover letter."""
        pass

    @abstractmethod
    async def get_by_id(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[CoverLetter]:
        """Fetch a specific cover letter with strict user ownership validation."""
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
    ) -> Tuple[List[CoverLetter], int]:
        """List cover letters for a user with optional filters and total count."""
        pass

    @abstractmethod
    async def update(self, cover_letter: CoverLetter) -> CoverLetter:
        """Update an existing cover letter."""
        pass

    @abstractmethod
    async def delete(self, cover_letter: CoverLetter) -> None:
        """Delete a cover letter."""
        pass
