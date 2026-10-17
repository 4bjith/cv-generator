from datetime import timedelta
import pytest
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utc_now
from app.models.auth_session import AuthSession
from app.services.auth_service import hash_token


@pytest.mark.asyncio
async def test_auth_registration_persists_user(async_client: AsyncClient) -> None:
    """Verify registration creates a user in the database and returns tokens."""
    payload = {
        "email": "aarav.pg@example.com",
        "password": "StrongPassword123!",
        "full_name": "Aarav Mehta",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

    user = data["user"]
    assert user["email"] == "aarav.pg@example.com"
    assert user["full_name"] == "Aarav Mehta"
    assert "id" in user
    assert user["is_active"] is True
    # Ensure sensitive credentials are never leaked
    assert "password" not in user
    assert "password_hash" not in user


@pytest.mark.asyncio
async def test_auth_duplicate_registration_fails(async_client: AsyncClient) -> None:
    """Verify registering with a duplicate email returns 409 Conflict."""
    payload = {
        "email": "duplicate.pg@example.com",
        "password": "Password123!",
        "full_name": "Duplicate Candidate",
    }
    # Initial registration
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email
    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    error = res2.json()["error"]
    assert error["code"] == "EMAIL_ALREADY_EXISTS"
    assert "already exists" in error["message"]


@pytest.mark.asyncio
async def test_auth_login_success_and_failure(async_client: AsyncClient) -> None:
    """Verify login against persisted user credentials."""
    email = "login.pg@example.com"
    password = "CorrectPassword123!"

    # Register candidate
    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Login Test User"},
    )
    assert reg_res.status_code == 201

    # Valid login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == email

    # Invalid password login
    bad_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword!"},
    )
    assert bad_res.status_code == 401
    assert bad_res.json()["error"]["code"] == "INVALID_CREDENTIALS"

    # Non-existent user login
    missing_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "missing.pg@example.com", "password": password},
    )
    assert missing_res.status_code == 401
    assert missing_res.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_auth_get_me_authenticated_and_unauthenticated(async_client: AsyncClient) -> None:
    """Verify GET /api/v1/auth/me behavior."""
    email = "me.pg@example.com"
    password = "MyPassword123!"

    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Me User"},
    )
    access_token = reg_res.json()["access_token"]
    refresh_token = reg_res.json()["refresh_token"]

    # 1. Authenticated with valid Bearer access token
    me_res = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    user = me_res.json()
    assert user["email"] == email
    assert user["full_name"] == "Me User"

    # 2. Missing authorization header
    no_auth = await async_client.get("/api/v1/auth/me")
    assert no_auth.status_code == 401
    assert no_auth.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

    # 3. Invalid token
    bad_token = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer fake.jwt.token"},
    )
    assert bad_token.status_code == 401
    assert bad_token.json()["error"]["code"] == "INVALID_TOKEN"

    # 4. Refresh token passed to access-token endpoint
    wrong_type = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert wrong_type.status_code == 401
    assert wrong_type.json()["error"]["code"] == "INVALID_TOKEN_TYPE"


@pytest.mark.asyncio
async def test_auth_refresh_token_rotation_and_revocation(async_client: AsyncClient) -> None:
    """Verify refresh token rotation and ensure old refresh tokens cannot be reused."""
    email = "rotation.pg@example.com"
    password = "SecurePassword123!"

    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Rotation User"},
    )
    initial_refresh_token = reg_res.json()["refresh_token"]

    # 1. Rotate token via /refresh
    ref_res1 = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh_token},
    )
    assert ref_res1.status_code == 200
    ref_data1 = ref_res1.json()
    new_refresh_token = ref_data1["refresh_token"]
    assert new_refresh_token != initial_refresh_token

    # 2. Attempt to REUSE the old refresh token (MUST FAIL)
    reuse_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh_token},
    )
    assert reuse_res.status_code == 401
    assert reuse_res.json()["error"]["code"] == "REVOKED_REFRESH_TOKEN"

    # 3. Use the new refresh token (MUST SUCCEED)
    ref_res2 = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh_token},
    )
    assert ref_res2.status_code == 200


@pytest.mark.asyncio
async def test_auth_expired_session_rejected(async_client: AsyncClient, db_session: AsyncSession) -> None:
    """Verify that an expired refresh session is rejected."""
    email = "expired.pg@example.com"
    password = "ExpiredPassword123!"

    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Expired User"},
    )
    refresh_token = reg_res.json()["refresh_token"]
    token_hash = hash_token(refresh_token)

    # Manually expire the session in the database
    past_time = utc_now() - timedelta(days=1)
    await db_session.execute(
        update(AuthSession)
        .where(AuthSession.refresh_token_hash == token_hash)
        .values(expires_at=past_time)
    )
    await db_session.commit()

    # Attempt to refresh with expired session
    exp_res = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert exp_res.status_code == 401
    assert exp_res.json()["error"]["code"] == "INVALID_REFRESH_SESSION"


@pytest.mark.asyncio
async def test_auth_logout_revokes_session(async_client: AsyncClient) -> None:
    """Verify logout revokes active sessions and prevents subsequent refresh."""
    email = "logout.pg@example.com"
    password = "LogoutPassword123!"

    reg_res = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Logout User"},
    )
    access_token = reg_res.json()["access_token"]
    refresh_token = reg_res.json()["refresh_token"]

    # 1. Logout
    logout_res = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out."

    # 2. Attempt to refresh with the revoked token (MUST FAIL)
    post_logout_ref = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert post_logout_ref.status_code == 401
    assert post_logout_ref.json()["error"]["code"] == "REVOKED_REFRESH_TOKEN"
