import uuid
import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str = "candidate@example.com") -> dict:
    """Helper fixture to register a user and obtain authorization header."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "Job Seeker",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_job_target_success_and_retrieval(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "job_create_get@example.com")

    # 1. Create job target
    payload = {
        "title": "Senior Frontend Engineer",
        "company_name": "Lattice Systems",
        "location": "San Francisco, CA (Hybrid)",
        "job_description": "We are seeking a seasoned frontend engineer to lead our core product design system.",
        "source_url": "https://lattice.com/careers/senior-frontend",
        "user_notes": "Referral from teammate. Emphasize React 19 and component architecture.",
        "status": "saved",
    }
    create_res = await async_client.post("/api/v1/jobs", json=payload, headers=headers)
    assert create_res.status_code == 201
    job_data = create_res.json()
    assert job_data["title"] == "Senior Frontend Engineer"
    assert job_data["company_name"] == "Lattice Systems"
    assert job_data["location"] == "San Francisco, CA (Hybrid)"
    assert job_data["job_description"] == payload["job_description"]
    assert job_data["source_url"] == payload["source_url"]
    assert job_data["user_notes"] == payload["user_notes"]
    assert job_data["status"] == "saved"
    assert "id" in job_data
    assert "created_at" in job_data
    assert "updated_at" in job_data

    job_id = job_data["id"]

    # 2. Retrieve job target by ID
    get_res = await async_client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == job_id
    assert retrieved["title"] == "Senior Frontend Engineer"
    assert retrieved["company_name"] == "Lattice Systems"


@pytest.mark.asyncio
async def test_create_job_target_validation_failures(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "job_val_fail@example.com")

    # Empty / whitespace title -> 422
    res1 = await async_client.post(
        "/api/v1/jobs",
        json={"title": "   ", "company_name": "Acme", "job_description": "Valid description"},
        headers=headers,
    )
    assert res1.status_code == 422

    # Empty / whitespace company -> 422
    res2 = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Engineer", "company_name": "  ", "job_description": "Valid description"},
        headers=headers,
    )
    assert res2.status_code == 422

    # Invalid source URL format -> 422
    res3 = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Engineer",
            "company_name": "Acme",
            "job_description": "Valid description",
            "source_url": "ftp://not-http-link.com",
        },
        headers=headers,
    )
    assert res3.status_code == 422

    # Missing required description -> 422
    res4 = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Engineer", "company_name": "Acme"},
        headers=headers,
    )
    assert res4.status_code == 422


@pytest.mark.asyncio
async def test_list_job_targets_with_pagination_and_search(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "job_list_search@example.com")

    # Create 3 jobs
    jobs_to_create = [
        {"title": "Staff Backend Engineer", "company_name": "Stripe", "job_description": "Python, distributed systems, postgres", "location": "Seattle, WA"},
        {"title": "Senior Frontend Engineer", "company_name": "Vercel", "job_description": "Next.js, TypeScript, React", "location": "Remote"},
        {"title": "AI Platform Engineer", "company_name": "OpenAI", "job_description": "LLM orchestration, FastAPI", "location": "San Francisco, CA"},
    ]
    for j in jobs_to_create:
        res = await async_client.post("/api/v1/jobs", json=j, headers=headers)
        assert res.status_code == 201

    # 1. List all
    list_res = await async_client.get("/api/v1/jobs", headers=headers)
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # 2. Search query by company "Stripe"
    search_res1 = await async_client.get("/api/v1/jobs?search=stripe", headers=headers)
    assert search_res1.status_code == 200
    search_data1 = search_res1.json()
    assert search_data1["total"] == 1
    assert search_data1["items"][0]["company_name"] == "Stripe"

    # 3. Search query by title "Frontend"
    search_res2 = await async_client.get("/api/v1/jobs?search=frontend", headers=headers)
    assert search_res2.status_code == 200
    search_data2 = search_res2.json()
    assert search_data2["total"] == 1
    assert search_data2["items"][0]["title"] == "Senior Frontend Engineer"

    # 4. Search query by location "San Francisco"
    search_res3 = await async_client.get("/api/v1/jobs?search=francisco", headers=headers)
    assert search_res3.status_code == 200
    assert search_res3.json()["total"] == 1

    # 5. Pagination limit and offset
    page1 = await async_client.get("/api/v1/jobs?limit=2&offset=0", headers=headers)
    assert page1.status_code == 200
    p1_data = page1.json()
    assert len(p1_data["items"]) == 2
    assert p1_data["total"] == 3

    page2 = await async_client.get("/api/v1/jobs?limit=2&offset=2", headers=headers)
    assert page2.status_code == 200
    p2_data = page2.json()
    assert len(p2_data["items"]) == 1
    assert p2_data["total"] == 3


@pytest.mark.asyncio
async def test_job_target_status_filter_and_archiving(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "job_archive@example.com")

    # Create 2 jobs
    res1 = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Role 1", "company_name": "Company A", "job_description": "Description A", "status": "saved"},
        headers=headers,
    )
    job1_id = res1.json()["id"]

    res2 = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Role 2", "company_name": "Company B", "job_description": "Description B", "status": "saved"},
        headers=headers,
    )
    job2_id = res2.json()["id"]

    # Archive job 1
    patch_res = await async_client.patch(
        f"/api/v1/jobs/{job1_id}",
        json={"status": "archived"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "archived"

    # Filter by saved
    saved_res = await async_client.get("/api/v1/jobs?status=saved", headers=headers)
    assert saved_res.status_code == 200
    saved_items = saved_res.json()["items"]
    assert len(saved_items) == 1
    assert saved_items[0]["id"] == job2_id

    # Filter by archived
    archived_res = await async_client.get("/api/v1/jobs?status=archived", headers=headers)
    assert archived_res.status_code == 200
    archived_items = archived_res.json()["items"]
    assert len(archived_items) == 1
    assert archived_items[0]["id"] == job1_id

    # Unarchive back to saved
    unarchive_res = await async_client.patch(
        f"/api/v1/jobs/{job1_id}",
        json={"status": "saved"},
        headers=headers,
    )
    assert unarchive_res.status_code == 200
    assert unarchive_res.json()["status"] == "saved"


@pytest.mark.asyncio
async def test_update_and_delete_job_target(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "job_update_delete@example.com")

    # Create job
    create_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Junior Developer",
            "company_name": "Startup Inc",
            "location": "Boston, MA",
            "job_description": "Initial draft description",
            "user_notes": "First note",
        },
        headers=headers,
    )
    job_id = create_res.json()["id"]

    # Update title, location, notes, and description
    patch_res = await async_client.patch(
        f"/api/v1/jobs/{job_id}",
        json={
            "title": "Mid-Level Software Engineer",
            "location": "Remote, US",
            "job_description": "Updated comprehensive requirements",
            "user_notes": "Updated note with interview date",
        },
        headers=headers,
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["title"] == "Mid-Level Software Engineer"
    assert updated["location"] == "Remote, US"
    assert updated["job_description"] == "Updated comprehensive requirements"
    assert updated["user_notes"] == "Updated note with interview date"
    assert updated["company_name"] == "Startup Inc"  # unchanged

    # Delete job
    del_res = await async_client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify deleted -> 404
    get_res = await async_client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_cross_user_isolation_for_jobs(async_client: AsyncClient):
    # User A
    headers_a = await get_auth_headers(async_client, "user_a_jobs@example.com")
    res_a = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Private Role A", "company_name": "Company A", "job_description": "Secret Job A"},
        headers=headers_a,
    )
    job_a_id = res_a.json()["id"]

    # User B
    headers_b = await get_auth_headers(async_client, "user_b_jobs@example.com")

    # User B tries to GET User A's job -> 404
    get_res = await async_client.get(f"/api/v1/jobs/{job_a_id}", headers=headers_b)
    assert get_res.status_code == 404

    # User B tries to PATCH User A's job -> 404
    patch_res = await async_client.patch(
        f"/api/v1/jobs/{job_a_id}",
        json={"title": "Hacked Title"},
        headers=headers_b,
    )
    assert patch_res.status_code == 404

    # User B tries to DELETE User A's job -> 404
    del_res = await async_client.delete(f"/api/v1/jobs/{job_a_id}", headers=headers_b)
    assert del_res.status_code == 404

    # User B lists jobs -> should not see User A's job
    list_res = await async_client.get("/api/v1/jobs", headers=headers_b)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 0

    # Verify User A's job is still intact
    get_a = await async_client.get(f"/api/v1/jobs/{job_a_id}", headers=headers_a)
    assert get_a.status_code == 200
    assert get_a.json()["title"] == "Private Role A"


@pytest.mark.asyncio
async def test_unauthenticated_requests_rejected(async_client: AsyncClient):
    dummy_id = uuid.uuid4()

    # GET /api/v1/jobs
    res1 = await async_client.get("/api/v1/jobs")
    assert res1.status_code == 401

    # POST /api/v1/jobs
    res2 = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Test", "company_name": "Test", "job_description": "Test"},
    )
    assert res2.status_code == 401

    # GET /api/v1/jobs/{id}
    res3 = await async_client.get(f"/api/v1/jobs/{dummy_id}")
    assert res3.status_code == 401

    # PATCH /api/v1/jobs/{id}
    res4 = await async_client.patch(f"/api/v1/jobs/{dummy_id}", json={"title": "Test"})
    assert res4.status_code == 401

    # DELETE /api/v1/jobs/{id}
    res5 = await async_client.delete(f"/api/v1/jobs/{dummy_id}")
    assert res5.status_code == 401
