from functools import lru_cache
from typing import Optional

from app.ai.gemini_provider import GeminiProvider
from app.ai.interface import AIProviderInterface
from app.ai.mock_provider import MockAIProvider
from app.core.config import get_settings
from app.core.exceptions import InternalServerError
from app.core.logging import get_logger

logger = get_logger("app.ai.factory")


@lru_cache
def get_ai_provider() -> AIProviderInterface:
    """
    Factory creating configured AIProviderInterface instance.
    - If ai_provider == "gemini": Strictly requires GEMINI_API_KEY, raises error if absent.
    - If ai_provider == "auto":
        - In production/staging: Requires GEMINI_API_KEY; disallows silent mock fallback.
        - In dev: Uses Gemini if GEMINI_API_KEY is present; otherwise falls back to MockAIProvider.
        - In test: Always uses deterministic MockAIProvider.
    - If ai_provider == "mock": Allowed only in non-production/test environments.
    """
    settings = get_settings()
    provider_choice = getattr(settings, "ai_provider", "auto").lower()
    app_env = getattr(settings, "app_env", "development").lower()
    is_prod_or_staging = app_env in ("production", "staging")

    if provider_choice == "gemini":
        if not settings.gemini_api_key or not settings.gemini_api_key.strip():
            logger.error("AI_PROVIDER='gemini' selected but GEMINI_API_KEY is missing or empty.")
            raise InternalServerError(
                "Gemini AI provider was explicitly configured (AI_PROVIDER='gemini'), "
                "but GEMINI_API_KEY is missing or empty. Please set GEMINI_API_KEY."
            )
        logger.info(f"Initializing Google Gemini AI Provider (model={settings.gemini_model})")
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model,
            embedding_model=settings.gemini_embedding_model,
        )

    elif provider_choice == "auto":
        if is_prod_or_staging and (not settings.gemini_api_key or not settings.gemini_api_key.strip()):
            logger.error(
                f"Production/staging environment ({app_env}) with AI_PROVIDER='auto' has no GEMINI_API_KEY. "
                "Silent fallback to mock provider is prohibited."
            )
            raise InternalServerError(
                f"Running in {app_env} environment with AI_PROVIDER='auto', "
                "but GEMINI_API_KEY is not configured. Silent fallback to mock provider is prohibited in production/staging."
            )

        if settings.gemini_api_key and settings.gemini_api_key.strip() and app_env != "test":
            logger.info(f"Auto-selected Google Gemini AI Provider (model={settings.gemini_model})")
            return GeminiProvider(
                api_key=settings.gemini_api_key,
                model_name=settings.gemini_model,
                embedding_model=settings.gemini_embedding_model,
            )
        else:
            logger.info(f"Auto-selected Mock AI Provider (env={app_env}, api_key_configured={bool(settings.gemini_api_key)})")
            return MockAIProvider()

    elif provider_choice == "mock":
        if is_prod_or_staging:
            logger.error(f"AI_PROVIDER='mock' is prohibited in {app_env} environment.")
            raise InternalServerError(f"AI_PROVIDER='mock' is not permitted in {app_env} environment.")
        logger.info(f"Initializing Mock AI Provider (env={app_env})")
        return MockAIProvider()

    else:
        logger.warning(f"Unrecognized AI_PROVIDER '{provider_choice}', falling back to Mock AI Provider.")
        if is_prod_or_staging:
            raise InternalServerError(f"Invalid AI_PROVIDER '{provider_choice}' in {app_env} environment.")
        return MockAIProvider()


def clear_ai_provider_cache() -> None:
    """Clear cached AI provider singleton so runtime configuration changes take effect immediately."""
    get_ai_provider.cache_clear()
