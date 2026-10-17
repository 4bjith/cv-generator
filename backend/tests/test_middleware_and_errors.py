import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_generated_and_returned(async_client: AsyncClient) -> None:
    """Verify that every request receives an X-Request-ID response header."""
    response = await async_client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    req_id = response.headers["X-Request-ID"]
    assert req_id.startswith("req_")


@pytest.mark.asyncio
async def test_custom_request_id_preserved(async_client: AsyncClient) -> None:
    """Verify that a valid client-supplied X-Request-ID is preserved and returned."""
    custom_id = "test-correlation-id-9988"
    response = await async_client.get(
        "/api/v1/health/live",
        headers={"X-Request-ID": custom_id},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_security_headers_present(async_client: AsyncClient) -> None:
    """Verify standard security headers on all responses."""
    response = await async_client.get("/api/v1/health/live")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "strict-origin" in response.headers.get("Referrer-Policy", "")


@pytest.mark.asyncio
async def test_standard_404_error_contract(async_client: AsyncClient) -> None:
    """Verify that requesting an unmapped route returns standardized error JSON."""
    response = await async_client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404

    data = response.json()
    assert "error" in data
    error = data["error"]
    assert error["code"] == "NOT_FOUND"
    assert "message" in error
    assert "request_id" in error
    assert error["request_id"].startswith("req_")


@pytest.mark.asyncio
async def test_standard_422_validation_error_contract(async_client: AsyncClient) -> None:
    """Verify that invalid request payloads return structured validation error JSON."""
    # Send empty body to /register which requires email, password, full_name
    response = await async_client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422

    data = response.json()
    assert "error" in data
    error = data["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "details" in error
    assert isinstance(error["details"], list)
    assert len(error["details"]) > 0

    # Ensure field information is present in details
    field_names = [d["field"] for d in error["details"]]
    assert any("email" in f for f in field_names)
    assert any("password" in f for f in field_names)
