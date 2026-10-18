from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AIProviderInterface(ABC):
    """
    Abstract interface for AI intelligence providers.
    Supports text generation, structured output schema generation, and vector embeddings.
    Allows swappable implementations (Google Gemini, MockProvider, OpenAI, etc.).
    """

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate unstructured plain text response."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured output validated against a Pydantic schema."""
        pass

    @abstractmethod
    async def compute_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        """Compute vector embeddings for a list of text strings."""
        pass
