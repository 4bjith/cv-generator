from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from httpx import AsyncClient

from app.ai.factory import clear_ai_provider_cache, get_ai_provider
from app.ai.gemini_provider import GeminiProvider
from app.ai.mock_provider import MockAIProvider
from app.core.config import Settings, get_settings
from app.core.exceptions import InternalServerError
from app.core.logging import setup_logging
from app.schemas.tailoring import StructuredTailoringOutput


@pytest.fixture(autouse=True)
def reset_provider_cache():
    """Ensure AI provider factory cache is cleanly reset between tests."""
    clear_ai_provider_cache()
    yield
    clear_ai_provider_cache()


# ==============================================================================
# 1. Header-based Authentication and URL Credential Secrecy
# ==============================================================================

@pytest.mark.asyncio
async def test_gemini_provider_uses_header_auth_and_no_url_credentials():
    """
    Verify that GeminiProvider passes the API key in the x-goog-api-key header
    and never appends credentials to the request URL query parameters.
    """
    secret_key = "super_secret_production_gemini_api_key_12345"
    provider = GeminiProvider(api_key=secret_key, model_name="gemini-1.5-flash")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": "Generated response text."}]}}
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        # 1. Text generation test
        result = await provider.generate_text("Test prompt")
        assert result == "Generated response text."

        called_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        headers = kwargs.get("headers", {})

        # URL must be clean
        assert "?" not in called_url
        assert "key=" not in called_url
        assert secret_key not in called_url
        assert called_url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

        # Headers must contain x-goog-api-key
        assert headers.get("x-goog-api-key") == secret_key


@pytest.mark.asyncio
async def test_gemini_provider_embeddings_header_auth():
    """Verify embeddings requests use header authentication without query parameters."""
    secret_key = "secret_embedding_key_789"
    provider = GeminiProvider(api_key=secret_key, embedding_model="text-embedding-004")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "embeddings": [{"values": [0.1, 0.2, 0.3]}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await provider.compute_embeddings(["test embedding text"])
        assert len(result) == 1
        assert result[0] == [0.1, 0.2, 0.3]

        called_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
        headers = kwargs.get("headers", {})

        assert "?" not in called_url
        assert secret_key not in called_url
        assert headers.get("x-goog-api-key") == secret_key


# ==============================================================================
# 2. Retry Policy: Transient Errors vs Non-Retryable Client Errors
# ==============================================================================

@pytest.mark.asyncio
async def test_gemini_provider_does_not_retry_client_errors_400():
    """
    Verify that non-transient HTTP 400 Bad Request (such as API_KEY_INVALID)
    fails immediately on the first attempt and is NOT retried.
    """
    provider = GeminiProvider(api_key="invalid_key", max_retries=3)

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "API key not valid."
    mock_resp.json.return_value = {"error": {"code": 400, "message": "API key not valid."}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(InternalServerError) as exc_info:
            await provider.generate_text("Prompt")

        assert "Gemini API returned status 400" in str(exc_info.value)
        # MUST ONLY BE CALLED ONCE (no retry loop on 400)
        assert mock_post.call_count == 1


@pytest.mark.asyncio
async def test_gemini_provider_does_not_retry_client_errors_403():
    """Verify that HTTP 403 Forbidden is not retried."""
    provider = GeminiProvider(api_key="restricted_key", max_retries=3)

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "Permission denied or project quota disabled."
    mock_resp.json.return_value = {"error": {"code": 403, "message": "Permission denied"}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(InternalServerError) as exc_info:
            await provider.generate_text("Prompt")

        assert "403" in str(exc_info.value)
        assert mock_post.call_count == 1


@pytest.mark.asyncio
async def test_gemini_provider_retries_transient_429_rate_limit():
    """Verify that HTTP 429 rate limit is retried with backoff and succeeds on subsequent try."""
    provider = GeminiProvider(api_key="valid_key", max_retries=3)

    resp_429 = MagicMock()
    resp_429.status_code = 429

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Recovered after 429."}]}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        mock_post.side_effect = [resp_429, resp_200]

        result = await provider.generate_text("Prompt")
        assert result == "Recovered after 429."
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1


@pytest.mark.asyncio
async def test_gemini_provider_retries_transient_500_server_error():
    """Verify that HTTP 500 server error is retried and succeeds on recovery."""
    provider = GeminiProvider(api_key="valid_key", max_retries=3)

    resp_500 = MagicMock()
    resp_500.status_code = 500

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Recovered after 500."}]}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        mock_post.side_effect = [resp_500, resp_200]

        result = await provider.generate_text("Prompt")
        assert result == "Recovered after 500."
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1


@pytest.mark.asyncio
async def test_gemini_provider_retries_transient_network_timeout():
    """Verify that network TimeoutException is retried and succeeds on recovery."""
    provider = GeminiProvider(api_key="valid_key", max_retries=3)

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Recovered after timeout."}]}}]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        mock_post.side_effect = [httpx.TimeoutException("Connection timed out"), resp_200]

        result = await provider.generate_text("Prompt")
        assert result == "Recovered after timeout."
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1


# ==============================================================================
# 3. Logging Stability (No TypeError on standard logging)
# ==============================================================================

@pytest.mark.asyncio
async def test_gemini_provider_logging_does_not_crash_with_typeerror():
    """
    Verify that with active logging subsystem, error logging in GeminiProvider
    and MockAIProvider does not crash with TypeError (invalid kwargs).
    """
    setup_logging(level="DEBUG", log_format="json")

    provider = GeminiProvider(api_key="test_key", max_retries=1)

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Bad input"
    mock_resp.json.return_value = {"error": {"message": "Bad input"}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        # Should raise InternalServerError from API status, NOT a TypeError from logging!
        with pytest.raises(InternalServerError) as exc_info:
            await provider.generate_text("Prompt")

        assert "TypeError" not in str(exc_info.value)
        assert "400" in str(exc_info.value)


# ==============================================================================
# 4. Factory & Production Guardrails
# ==============================================================================

def test_ai_factory_gemini_requires_api_key():
    """Verify that selecting AI_PROVIDER='gemini' without an API key raises an immediate error."""
    mock_settings = MagicMock()
    mock_settings.ai_provider = "gemini"
    mock_settings.gemini_api_key = None
    mock_settings.app_env = "development"

    with patch("app.ai.factory.get_settings", return_value=mock_settings):
        clear_ai_provider_cache()
        with pytest.raises(InternalServerError) as exc_info:
            get_ai_provider()

        assert "GEMINI_API_KEY is missing or empty" in str(exc_info.value)


def test_ai_factory_production_prohibits_mock():
    """Verify that AI_PROVIDER='mock' is strictly prohibited in production."""
    mock_settings = MagicMock()
    mock_settings.ai_provider = "mock"
    mock_settings.app_env = "production"

    with patch("app.ai.factory.get_settings", return_value=mock_settings):
        clear_ai_provider_cache()
        with pytest.raises(InternalServerError) as exc_info:
            get_ai_provider()

        assert "AI_PROVIDER='mock' is not permitted in production" in str(exc_info.value)


def test_ai_factory_production_auto_disallows_silent_mock_fallback():
    """
    Verify that in production, AI_PROVIDER='auto' without an API key raises
    an error rather than silently returning MockAIProvider.
    """
    mock_settings = MagicMock()
    mock_settings.ai_provider = "auto"
    mock_settings.gemini_api_key = None
    mock_settings.app_env = "production"

    with patch("app.ai.factory.get_settings", return_value=mock_settings):
        clear_ai_provider_cache()
        with pytest.raises(InternalServerError) as exc_info:
            get_ai_provider()

        assert "Silent fallback to mock provider is prohibited" in str(exc_info.value)


def test_ai_factory_dev_auto_allows_mock_fallback():
    """Verify that in development, AI_PROVIDER='auto' without an API key falls back to mock."""
    mock_settings = MagicMock()
    mock_settings.ai_provider = "auto"
    mock_settings.gemini_api_key = None
    mock_settings.app_env = "development"

    with patch("app.ai.factory.get_settings", return_value=mock_settings):
        clear_ai_provider_cache()
        provider = get_ai_provider()
        assert isinstance(provider, MockAIProvider)


def test_settings_production_security_validation():
    """Verify Pydantic model validator enforces AI credentials in production settings."""
    # Production with mock provider must fail
    with pytest.raises(ValueError, match="AI_PROVIDER='mock' is not permitted"):
        Settings(
            app_env="production",
            jwt_secret_key="x" * 32,
            database_url="postgresql+asyncpg://admin:pass123@prod.db:5432/ai_cv_maker",
            ai_provider="mock",
        )

    # Production with auto provider but no API key must fail
    with pytest.raises(ValueError, match="GEMINI_API_KEY must be configured"):
        Settings(
            app_env="production",
            jwt_secret_key="x" * 32,
            database_url="postgresql+asyncpg://admin:pass123@prod.db:5432/ai_cv_maker",
            ai_provider="auto",
            gemini_api_key=None,
        )

    # Production with valid credentials succeeds
    valid_settings = Settings(
        app_env="production",
        jwt_secret_key="x" * 32,
        database_url="postgresql+asyncpg://admin:pass123@prod.db:5432/ai_cv_maker",
        ai_provider="gemini",
        gemini_api_key="valid-prod-key-12345",
    )
    assert valid_settings.is_production is True
    assert valid_settings.gemini_api_key == "valid-prod-key-12345"


# ==============================================================================
# 5. Safe Health Readiness Metadata
# ==============================================================================

@pytest.mark.asyncio
async def test_readiness_probe_exposes_safe_ai_metadata(async_client: AsyncClient):
    """
    Verify GET /api/v1/health/ready returns safe AI configuration metadata
    (provider, model, configured boolean) without leaking secrets.
    """
    response = await async_client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "ai" in data
    ai_meta = data["ai"]

    assert "provider" in ai_meta
    assert "model" in ai_meta
    assert "embedding_model" in ai_meta
    assert "configured" in ai_meta
    assert isinstance(ai_meta["configured"], bool)

    # NEVER expose actual key or secret fragments
    raw_response = response.text
    assert "api_key" not in raw_response
    assert "secret" not in raw_response.lower()
