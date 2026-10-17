from unittest.mock import patch
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_check(async_client: AsyncClient) -> None:
    """Verify GET /api/v1/health/live returns 200 and status ok without requiring database."""
    response = await async_client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_readiness_check_healthy(async_client: AsyncClient) -> None:
    """Verify GET /api/v1/health/ready returns 200 and indicates application and database are healthy."""
    response = await async_client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"]["application"] == "ok"
    assert data["checks"]["database"] == "ok"
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_readiness_check_database_unhealthy(async_client: AsyncClient) -> None:
    """Verify GET /api/v1/health/ready returns 503 when database connectivity fails."""
    with patch("app.api.routes.health.check_database_health", return_value=False):
        response = await async_client.get("/api/v1/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["database"] == "unavailable"


@pytest.mark.asyncio
async def test_legacy_health_check(async_client: AsyncClient) -> None:
    """Verify backward compatibility for GET /api/health."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-cv-maker-backend",
    }
