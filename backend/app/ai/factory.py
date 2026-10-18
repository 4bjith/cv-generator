from functools import lru_cache
from typing import Optional

from app.ai.gemini_provider import GeminiProvider
from app.ai.interface import AIProviderInterface
from app.ai.mock_provider import MockAIProvider
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("app.ai.factory")


@lru_cache
def get_ai_provider() -> AIProviderInterface:
    """
    Factory creating configured AIProviderInterface instance.
    - If ai_provider == "gemini" or ("auto" and gemini_api_key is set and app_env != "test"): uses GeminiProvider.
    - Otherwise uses deterministic MockAIProvider.
    """
    settings = get_settings()
    provider_choice = getattr(settings, "ai_provider", "auto").lower()

    if provider_choice == "gemini":
        logger.info("Initializing Google Gemini AI Provider", model=settings.gemini_model)
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model,
            embedding_model=settings.gemini_embedding_model,
        )
    elif provider_choice == "auto":
        if settings.gemini_api_key and settings.app_env != "test":
            logger.info("Auto-selected Gemini AI Provider (API key present)", model=settings.gemini_model)
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model_name=settings.gemini_model,
                embedding_model=settings.gemini_embedding_model,
            )
        else:
            logger.info("Auto-selected Mock AI Provider (test environment or no API key)")
            return MockAIProvider()
    else:
        logger.info("Initializing Mock AI Provider", mode=provider_choice)
        return MockAIProvider()
