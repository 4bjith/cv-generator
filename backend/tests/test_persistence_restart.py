import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.db.session import get_db_session
from tests.conftest import override_get_db_session


@pytest.mark.asyncio
async def test_persistence_across_app_restart() -> None:
    """Verify that user records created during one app session persist across application restarts."""
    email = "restart.persistent@example.com"
    password = "RestartPassword123!"
    full_name = "Persistent Candidate"

    # --- Session 1: Client starts, registers a user, then shuts down ---
    transport_1 = ASGITransport(app=app)
    app.dependency_overrides[get_db_session] = override_get_db_session
    async with AsyncClient(transport=transport_1, base_url="http://testserver") as client_1:
        reg_res = await client_1.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": full_name},
        )
        assert reg_res.status_code == 201
        user_id = reg_res.json()["user"]["id"]

    # --- Session 2: Fresh client instance (simulating application restart) ---
    transport_2 = ASGITransport(app=app)
    async with AsyncClient(transport=transport_2, base_url="http://testserver") as client_2:
        # Login using the credentials from Session 1
        login_res = await client_2.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["user"]["id"] == user_id
        assert login_data["user"]["email"] == email

        # Access /me with the new session's token
        access_token = login_data["access_token"]
        me_res = await client_2.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email
        assert me_res.json()["full_name"] == full_name


@pytest.mark.asyncio
async def test_logout_persistence_across_app_restart() -> None:
    """Verify that session revocation (logout) persists in PostgreSQL across application restarts."""
    email = "logout.restart@example.com"
    password = "LogoutPassword123!"

    # --- Session 1: Register and login, then logout ---
    transport_1 = ASGITransport(app=app)
    app.dependency_overrides[get_db_session] = override_get_db_session
    async with AsyncClient(transport=transport_1, base_url="http://testserver") as client_1:
        reg_res = await client_1.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": "Logout Restart User"},
        )
        assert reg_res.status_code == 201
        access_token = reg_res.json()["access_token"]
        refresh_token = reg_res.json()["refresh_token"]

        # Logout in session 1
        logout_res = await client_1.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert logout_res.status_code == 200

    # --- Session 2: Fresh client (simulating server reboot) ---
    transport_2 = ASGITransport(app=app)
    async with AsyncClient(transport=transport_2, base_url="http://testserver") as client_2:
        # Attempt to use the refresh token from before restart
        refresh_res = await client_2.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        # MUST BE REJECTED because revocation was persisted in PostgreSQL
        assert refresh_res.status_code == 401
        assert refresh_res.json()["error"]["code"] == "REVOKED_REFRESH_TOKEN"
