from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.job_target import JobExtractionResult


class IJobExtractor(ABC):
    """Abstract interface for job description requirement extraction."""

    @abstractmethod
    async def extract(
        self,
        text: str,
        title: Optional[str] = None,
        company: Optional[str] = None,
    ) -> JobExtractionResult:
        """Extract structured requirements, seniority, employment type, and keywords from job description text."""
        pass
