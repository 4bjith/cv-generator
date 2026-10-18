"""
Focused Live-Provider Integration and Readiness Verification Suite.

Tests live Google Gemini API interactions against the configured provider:
1. Live text generation
2. Live structured output for CV tailoring (StructuredTailoringOutput)
3. Live structured output for Cover Letter generation (StructuredCoverLetterOutput)
4. Live vector embeddings (gemini-embedding-001)
5. Sanitized handling of quota errors, timeouts, and provider failures
"""

import os
import pytest
from app.core.config import get_settings
from app.ai.gemini_provider import GeminiProvider
from app.core.exceptions import InternalServerError
from app.schemas.tailoring import StructuredTailoringOutput
from app.schemas.cover_letter import StructuredCoverLetterOutput


@pytest.fixture
def live_gemini_provider():
    settings = get_settings()
    api_key = settings.gemini_api_key
    if not api_key or not api_key.strip():
        pytest.skip("GEMINI_API_KEY is not configured in environment or backend/.env.")
    
    return GeminiProvider(
        api_key=api_key,
        model_name=settings.gemini_model or "gemini-flash-latest",
        embedding_model=settings.gemini_embedding_model or "gemini-embedding-001",
        timeout=30.0,
        max_retries=1,
    )


@pytest.mark.asyncio
async def test_live_gemini_text_generation(live_gemini_provider: GeminiProvider):
    """Verifies live Gemini text generation or captures exact quota limitation."""
    try:
        result = await live_gemini_provider.generate_text(
            prompt="Respond strictly with the single word: INTEGRATION_VERIFIED",
            max_tokens=50,
        )
        assert "INTEGRATION_VERIFIED" in result.strip()
    except InternalServerError as e:
        err_str = str(e)
        # Ensure API key is NEVER exposed in the error message
        assert live_gemini_provider.api_key not in err_str
        if "quota" in err_str.lower() or "rate limit" in err_str.lower():
            pytest.skip(f"Live Gemini text generation BLOCKED due to external quota: {err_str}")
        raise


@pytest.mark.asyncio
async def test_live_gemini_structured_cv_tailoring(live_gemini_provider: GeminiProvider):
    """Verifies live Gemini structured output adhering to StructuredTailoringOutput schema."""
    # 1. Verify schema dereferencing inlines $defs and removes invalid keywords
    raw_schema = StructuredTailoringOutput.model_json_schema()
    prepared_schema = live_gemini_provider._prepare_gemini_schema(raw_schema)
    assert "$defs" not in prepared_schema
    assert "title" not in prepared_schema
    assert prepared_schema["type"] == "object"

    try:
        result = await live_gemini_provider.generate_structured(
            prompt=(
                "Tailor candidate summary for Lead Distributed Systems Architect. "
                "Candidate has 9 years experience in Go and Raft consensus."
            ),
            schema=StructuredTailoringOutput,
        )
        assert isinstance(result, StructuredTailoringOutput)
        assert len(result.tailored_summary) > 10
    except InternalServerError as e:
        err_str = str(e)
        assert live_gemini_provider.api_key not in err_str
        if "quota" in err_str.lower() or "rate limit" in err_str.lower():
            pytest.skip(f"Live Gemini CV tailoring structured output BLOCKED due to external quota: {err_str}")
        raise


@pytest.mark.asyncio
async def test_live_gemini_structured_cover_letter(live_gemini_provider: GeminiProvider):
    """Verifies live Gemini structured output adhering to StructuredCoverLetterOutput schema."""
    # 1. Verify schema dereferencing inlines nested $defs (e.g. FactualClaimItem)
    raw_schema = StructuredCoverLetterOutput.model_json_schema()
    prepared_schema = live_gemini_provider._prepare_gemini_schema(raw_schema)
    assert "$defs" not in prepared_schema
    assert "title" not in prepared_schema
    assert prepared_schema["type"] == "object"

    try:
        result = await live_gemini_provider.generate_structured(
            prompt="Generate a 2-paragraph cover letter for Senior SRE at CloudCorp.",
            schema=StructuredCoverLetterOutput,
        )
        assert isinstance(result, StructuredCoverLetterOutput)
        assert len(result.opening) > 10
    except InternalServerError as e:
        err_str = str(e)
        assert live_gemini_provider.api_key not in err_str
        if "quota" in err_str.lower() or "rate limit" in err_str.lower():
            pytest.skip(f"Live Gemini Cover Letter structured output BLOCKED due to external quota: {err_str}")
        raise


@pytest.mark.asyncio
async def test_live_gemini_embeddings_success(live_gemini_provider: GeminiProvider):
    """Verifies live vector embeddings with real Google Gemini embedding model."""
    embeddings = await live_gemini_provider.compute_embeddings([
        "Distributed consensus Raft protocol implementation in Go",
        "Kubernetes container orchestration and service mesh telemetry",
    ])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 3072
    assert isinstance(embeddings[0][0], float)


@pytest.mark.asyncio
async def test_live_gemini_sanitized_errors_and_secrecy(live_gemini_provider: GeminiProvider):
    """Verifies that API keys and secrets are NEVER exposed in headers, URLs, or error messages."""
    headers = live_gemini_provider._get_headers()
    assert headers["x-goog-api-key"] == live_gemini_provider.api_key
    assert "Authorization" not in headers

    # Test error handling on bad model / invalid request
    bad_provider = GeminiProvider(
        api_key=live_gemini_provider.api_key,
        model_name="non-existent-model-xyz",
        timeout=10.0,
        max_retries=1,
    )
    with pytest.raises(InternalServerError) as exc_info:
        await bad_provider.generate_text("test")

    err_message = str(exc_info.value)
    # Confirm key does not appear anywhere in error message
    assert live_gemini_provider.api_key not in err_message
    assert "non-existent-model-xyz" in err_message
