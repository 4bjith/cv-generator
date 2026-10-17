import uuid
import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str = "candidate@example.com") -> dict:
    """Helper to register a user and obtain authorization header."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "CV Version User",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def setup_candidate_profile(client: AsyncClient, headers: dict) -> dict:
    """Helper to initialize a complete candidate profile with experiences, skills, and projects."""
    profile_payload = {
        "first_name": "Aarav",
        "last_name": "Mehta",
        "professional_headline": "Lead Systems Architect & Full Stack Engineer",
        "email": "aarav.mehta@example.com",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "primary_title": "Staff Engineer",
        "career_level": "senior",
        "base_summary": "Architecting resilient distributed systems and enterprise React web platforms.",
    }
    res = await client.post("/api/v1/profile", json=profile_payload, headers=headers)
    assert res.status_code == 201

    # Add an experience
    exp_res = await client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Stripe",
            "position": "Senior Software Engineer",
            "start_date": "2022-01-01",
            "is_current": True,
            "description": "Led billing infrastructure modernization.",
            "responsibilities": ["Designed event streaming pipelines", "Mentored 4 junior engineers"],
            "technologies": ["Python", "FastAPI", "React", "PostgreSQL"],
        },
        headers=headers,
    )
    assert exp_res.status_code == 201

    # Add a skill
    skill_res = await client.post(
        "/api/v1/profile/skills",
        json={
            "name": "FastAPI",
            "category": "backend",
            "proficiency": "expert",
            "years_of_experience": 5.0,
        },
        headers=headers,
    )
    assert skill_res.status_code == 201

    # Add a project
    proj_res = await client.post(
        "/api/v1/profile/projects",
        json={
            "name": "Distributed Job Scheduler",
            "role": "Creator & Lead Dev",
            "description": "High-throughput asynchronous task engine.",
            "technologies": ["Python", "Redis", "PostgreSQL"],
        },
        headers=headers,
    )
    assert proj_res.status_code == 201

    # Retrieve full profile
    get_profile_res = await client.get("/api/v1/profile", headers=headers)
    assert get_profile_res.status_code == 200
    return get_profile_res.json()


@pytest.mark.asyncio
async def test_create_cv_version_from_profile_success(async_client: AsyncClient):
    """Test creating a CV version snapshot from an existing CandidateProfile."""
    headers = await get_auth_headers(async_client, "cv_create_success@example.com")
    await setup_candidate_profile(async_client, headers)

    create_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Stripe Staff Engineer V1"},
        headers=headers,
    )
    assert create_res.status_code == 201
    cv_data = create_res.json()

    assert cv_data["name"] == "Stripe Staff Engineer V1"
    assert cv_data["status"] == "draft"
    assert cv_data["job_target_id"] is None
    assert "id" in cv_data

    # Verify snapshot content
    snapshot = cv_data["content_snapshot"]
    assert snapshot["basics"]["first_name"] == "Aarav"
    assert snapshot["basics"]["last_name"] == "Mehta"
    assert snapshot["basics"]["professional_headline"] == "Lead Systems Architect & Full Stack Engineer"
    assert len(snapshot["experiences"]) == 1
    assert snapshot["experiences"][0]["company"] == "Stripe"
    assert len(snapshot["skills"]) == 1
    assert snapshot["skills"][0]["name"] == "FastAPI"
    assert len(snapshot["projects"]) == 1
    assert snapshot["projects"][0]["name"] == "Distributed Job Scheduler"


@pytest.mark.asyncio
async def test_create_cv_version_requires_profile(async_client: AsyncClient):
    """Test that creating a CV version fails with 404 if the user has not created a CandidateProfile."""
    headers = await get_auth_headers(async_client, "cv_no_profile@example.com")

    res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Profileless CV"},
        headers=headers,
    )
    assert res.status_code == 404
    error = res.json()
    assert error["error"]["code"] == "PROFILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_cv_version_with_job_target_success(async_client: AsyncClient):
    """Test creating a CV version linked to a user's JobTarget opportunity."""
    headers = await get_auth_headers(async_client, "cv_with_job@example.com")
    await setup_candidate_profile(async_client, headers)

    # 1. Create a job target
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Principal Architect",
            "company_name": "Vercel",
            "job_description": "Architect next generation serverless infrastructure.",
        },
        headers=headers,
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 2. Create CV version linked to job target
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={
            "name": "Vercel Tailored CV",
            "job_target_id": job_id,
        },
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_data = cv_res.json()
    assert cv_data["job_target_id"] == job_id
    assert cv_data["job_target_title"] == "Principal Architect"
    assert cv_data["job_target_company"] == "Vercel"


@pytest.mark.asyncio
async def test_create_cv_version_rejects_cross_user_job_target(async_client: AsyncClient):
    """Test that creating a CV version referencing another user's JobTarget is rejected with 404."""
    headers_a = await get_auth_headers(async_client, "user_a_cv_job@example.com")
    headers_b = await get_auth_headers(async_client, "user_b_cv_job@example.com")
    await setup_candidate_profile(async_client, headers_b)

    # User A creates a job target
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Confidential Role",
            "company_name": "Secret Corp",
            "job_description": "Top secret job description.",
        },
        headers=headers_a,
    )
    assert job_res.status_code == 201
    job_a_id = job_res.json()["id"]

    # User B attempts to link User A's job target
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={
            "name": "Unauthorized Linked CV",
            "job_target_id": job_a_id,
        },
        headers=headers_b,
    )
    assert cv_res.status_code == 404
    assert cv_res.json()["error"]["code"] == "JOB_TARGET_NOT_FOUND"


@pytest.mark.asyncio
async def test_cv_version_snapshot_immutability_on_profile_changes(async_client: AsyncClient):
    """Critical test: Modifying the master CandidateProfile does NOT alter existing CV snapshots."""
    headers = await get_auth_headers(async_client, "cv_immutability@example.com")
    await setup_candidate_profile(async_client, headers)

    # 1. Create CV version snapshot
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Immutable Base Version"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]

    # 2. Modify master candidate profile
    patch_profile_res = await async_client.patch(
        "/api/v1/profile",
        json={
            "first_name": "Rohan",
            "professional_headline": "Completely Altered Master Headline",
            "base_summary": "Brand new master summary text.",
        },
        headers=headers,
    )
    assert patch_profile_res.status_code == 200

    # Add a second experience to master profile
    await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "New Corp",
            "position": "Director of Engineering",
            "start_date": "2025-01-01",
            "is_current": True,
        },
        headers=headers,
    )

    # 3. Retrieve the existing CV version snapshot
    get_cv_res = await async_client.get(f"/api/v1/cv/versions/{cv_id}", headers=headers)
    assert get_cv_res.status_code == 200
    cv_data = get_cv_res.json()
    snapshot = cv_data["content_snapshot"]

    # Verify snapshot STILL has the original values
    assert snapshot["basics"]["first_name"] == "Aarav"
    assert snapshot["basics"]["professional_headline"] == "Lead Systems Architect & Full Stack Engineer"
    assert snapshot["basics"]["base_summary"] == "Architecting resilient distributed systems and enterprise React web platforms."
    assert len(snapshot["experiences"]) == 1
    assert snapshot["experiences"][0]["company"] == "Stripe"


@pytest.mark.asyncio
async def test_update_cv_version_does_not_mutate_master_profile(async_client: AsyncClient):
    """Critical test: Updating a CV version snapshot does NOT mutate the master CandidateProfile."""
    headers = await get_auth_headers(async_client, "cv_update_isolation@example.com")
    await setup_candidate_profile(async_client, headers)

    # 1. Create CV version
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Targeted Pitch V1"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]
    snapshot = cv_res.json()["content_snapshot"]

    # 2. Update CV version snapshot specific content
    snapshot["basics"]["professional_headline"] = "Customized Tailored Headline for Target Company"
    snapshot["basics"]["base_summary"] = "Version-specific custom pitch for hiring manager."
    update_res = await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={
            "name": "Targeted Pitch V1.1",
            "status": "ready",
            "content_snapshot": snapshot,
        },
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Targeted Pitch V1.1"
    assert update_res.json()["status"] == "ready"
    assert update_res.json()["content_snapshot"]["basics"]["professional_headline"] == "Customized Tailored Headline for Target Company"

    # 3. Retrieve master candidate profile and assert it is pristine
    master_profile_res = await async_client.get("/api/v1/profile", headers=headers)
    assert master_profile_res.status_code == 200
    master = master_profile_res.json()
    assert master["professional_headline"] == "Lead Systems Architect & Full Stack Engineer"
    assert master["base_summary"] == "Architecting resilient distributed systems and enterprise React web platforms."


@pytest.mark.asyncio
async def test_duplicate_cv_version_produces_independent_record_and_snapshot(async_client: AsyncClient):
    """Test duplicating a CV version creates an independent record and deep-copied snapshot."""
    headers = await get_auth_headers(async_client, "cv_duplicate@example.com")
    await setup_candidate_profile(async_client, headers)

    # 1. Create original CV version
    orig_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Original CV"},
        headers=headers,
    )
    assert orig_res.status_code == 201
    orig_id = orig_res.json()["id"]

    # 2. Duplicate CV version
    dup_res = await async_client.post(
        f"/api/v1/cv/versions/{orig_id}/duplicate",
        json={"name": "Duplicated Clone CV"},
        headers=headers,
    )
    assert dup_res.status_code == 201
    dup_data = dup_res.json()
    dup_id = dup_data["id"]
    assert dup_id != orig_id
    assert dup_data["name"] == "Duplicated Clone CV"
    assert dup_data["status"] == "draft"

    # 3. Modify cloned snapshot
    cloned_snapshot = dup_data["content_snapshot"]
    cloned_snapshot["basics"]["first_name"] = "CloneName"
    await async_client.patch(
        f"/api/v1/cv/versions/{dup_id}",
        json={"content_snapshot": cloned_snapshot},
        headers=headers,
    )

    # 4. Assert original CV version snapshot is unchanged
    get_orig = await async_client.get(f"/api/v1/cv/versions/{orig_id}", headers=headers)
    assert get_orig.status_code == 200
    assert get_orig.json()["content_snapshot"]["basics"]["first_name"] == "Aarav"


@pytest.mark.asyncio
async def test_archive_and_restore_cv_version(async_client: AsyncClient):
    """Test archiving and restoring CV versions."""
    headers = await get_auth_headers(async_client, "cv_archive_restore@example.com")
    await setup_candidate_profile(async_client, headers)

    # Create CV
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Version to Archive"},
        headers=headers,
    )
    cv_id = cv_res.json()["id"]
    assert cv_res.json()["status"] == "draft"

    # Archive
    arch_res = await async_client.post(f"/api/v1/cv/versions/{cv_id}/archive", headers=headers)
    assert arch_res.status_code == 200
    assert arch_res.json()["status"] == "archived"

    # Restore
    rest_res = await async_client.post(f"/api/v1/cv/versions/{cv_id}/restore", headers=headers)
    assert rest_res.status_code == 200
    assert rest_res.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_delete_cv_version(async_client: AsyncClient):
    """Test deleting a CV version."""
    headers = await get_auth_headers(async_client, "cv_delete@example.com")
    await setup_candidate_profile(async_client, headers)

    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Temporary Version"},
        headers=headers,
    )
    cv_id = cv_res.json()["id"]

    del_res = await async_client.delete(f"/api/v1/cv/versions/{cv_id}", headers=headers)
    assert del_res.status_code == 204

    get_res = await async_client.get(f"/api/v1/cv/versions/{cv_id}", headers=headers)
    assert get_res.status_code == 404
    assert get_res.json()["error"]["code"] == "CV_VERSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_deleting_job_target_sets_job_target_id_null_and_preserves_cv_version(async_client: AsyncClient):
    """Critical foreign key test: Deleting a JobTarget sets job_target_id to NULL and preserves CVVersion."""
    headers = await get_auth_headers(async_client, "cv_job_delete_null@example.com")
    await setup_candidate_profile(async_client, headers)

    # 1. Create a JobTarget
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Lead Platform Engineer",
            "company_name": "Datadog",
            "job_description": "Datadog platform engineering position.",
        },
        headers=headers,
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 2. Create CVVersion linked to this JobTarget
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={
            "name": "Datadog Platform CV",
            "job_target_id": job_id,
        },
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]
    assert cv_res.json()["job_target_id"] == job_id

    # 3. Delete the JobTarget
    del_job_res = await async_client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
    assert del_job_res.status_code == 204

    # 4. Retrieve CVVersion and verify it STILL exists with job_target_id == None
    get_cv_res = await async_client.get(f"/api/v1/cv/versions/{cv_id}", headers=headers)
    assert get_cv_res.status_code == 200
    cv_data = get_cv_res.json()
    assert cv_data["id"] == cv_id
    assert cv_data["job_target_id"] is None
    assert cv_data["job_target_title"] is None
    assert cv_data["job_target_company"] is None


@pytest.mark.asyncio
async def test_cross_user_cv_version_isolation(async_client: AsyncClient):
    """Test that users cannot access, update, duplicate, archive, restore, or delete other users' CV versions."""
    headers_a = await get_auth_headers(async_client, "user_a_isolation@example.com")
    headers_b = await get_auth_headers(async_client, "user_b_isolation@example.com")
    await setup_candidate_profile(async_client, headers_a)
    await setup_candidate_profile(async_client, headers_b)

    # User A creates CV version
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "User A Private CV"},
        headers=headers_a,
    )
    assert cv_res.status_code == 201
    cv_a_id = cv_res.json()["id"]

    # User B tries GET -> 404
    get_res = await async_client.get(f"/api/v1/cv/versions/{cv_a_id}", headers=headers_b)
    assert get_res.status_code == 404
    assert get_res.json()["error"]["code"] == "CV_VERSION_NOT_FOUND"

    # User B tries PATCH -> 404
    patch_res = await async_client.patch(
        f"/api/v1/cv/versions/{cv_a_id}",
        json={"name": "Hacked Name"},
        headers=headers_b,
    )
    assert patch_res.status_code == 404

    # User B tries duplicate -> 404
    dup_res = await async_client.post(
        f"/api/v1/cv/versions/{cv_a_id}/duplicate",
        json={"name": "Stolen CV"},
        headers=headers_b,
    )
    assert dup_res.status_code == 404

    # User B tries archive -> 404
    arch_res = await async_client.post(f"/api/v1/cv/versions/{cv_a_id}/archive", headers=headers_b)
    assert arch_res.status_code == 404

    # User B tries restore -> 404
    rest_res = await async_client.post(f"/api/v1/cv/versions/{cv_a_id}/restore", headers=headers_b)
    assert rest_res.status_code == 404

    # User B tries DELETE -> 404
    del_res = await async_client.delete(f"/api/v1/cv/versions/{cv_a_id}", headers=headers_b)
    assert del_res.status_code == 404


@pytest.mark.asyncio
async def test_cv_version_list_filtering_and_pagination(async_client: AsyncClient):
    """Test listing CV versions with status, search, and job target filters and pagination."""
    headers = await get_auth_headers(async_client, "cv_list_filters@example.com")
    await setup_candidate_profile(async_client, headers)

    # Create 2 job targets
    job1 = (await async_client.post("/api/v1/jobs", json={"title": "Role 1", "company_name": "Co 1", "job_description": "Desc 1"}, headers=headers)).json()
    job2 = (await async_client.post("/api/v1/jobs", json={"title": "Role 2", "company_name": "Co 2", "job_description": "Desc 2"}, headers=headers)).json()

    # Create 3 versions
    v1 = (await async_client.post("/api/v1/cv/versions", json={"name": "Backend Specialist", "job_target_id": job1["id"]}, headers=headers)).json()
    v2 = (await async_client.post("/api/v1/cv/versions", json={"name": "Frontend Specialist", "job_target_id": job2["id"]}, headers=headers)).json()
    v3 = (await async_client.post("/api/v1/cv/versions", json={"name": "General Tech Lead"}, headers=headers)).json()

    # Archive v2
    await async_client.post(f"/api/v1/cv/versions/{v2['id']}/archive", headers=headers)

    # 1. List all
    all_res = await async_client.get("/api/v1/cv/versions", headers=headers)
    assert all_res.status_code == 200
    assert all_res.json()["total"] == 3

    # 2. Filter by status == archived
    arch_res = await async_client.get("/api/v1/cv/versions?status=archived", headers=headers)
    assert arch_res.status_code == 200
    assert arch_res.json()["total"] == 1
    assert arch_res.json()["items"][0]["name"] == "Frontend Specialist"

    # 3. Filter by search == Backend
    search_res = await async_client.get("/api/v1/cv/versions?search=Backend", headers=headers)
    assert search_res.status_code == 200
    assert search_res.json()["total"] == 1
    assert search_res.json()["items"][0]["name"] == "Backend Specialist"

    # 4. Filter by job_target_id == job1
    job_filter_res = await async_client.get(f"/api/v1/cv/versions?job_target_id={job1['id']}", headers=headers)
    assert job_filter_res.status_code == 200
    assert job_filter_res.json()["total"] == 1
    assert job_filter_res.json()["items"][0]["name"] == "Backend Specialist"

    # 5. Pagination
    paged_res = await async_client.get("/api/v1/cv/versions?limit=1&offset=0", headers=headers)
    assert paged_res.status_code == 200
    assert paged_res.json()["total"] == 3
    assert len(paged_res.json()["items"]) == 1
    assert paged_res.json()["limit"] == 1
    assert paged_res.json()["offset"] == 0


# ==========================================
# Phase 2.3 Hybrid Schema & Normalizer Tests
# ==========================================

@pytest.mark.asyncio
async def test_legacy_snapshot_normalization(async_client: AsyncClient):
    """Test updating a CV version with a legacy snapshot normalizes into canonical 2.0.0 format."""
    headers = await get_auth_headers(async_client, "cv_legacy_norm@example.com")
    await setup_candidate_profile(async_client, headers)

    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Legacy Snapshot Version"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]

    # Provide legacy snapshot payload (experiences, certifications, achievements, flat location)
    legacy_payload = {
        "basics": {
            "first_name": "Marcus",
            "last_name": "Aurelius",
            "professional_headline": "Philosophy & Distributed Systems",
            "city": "Rome",
            "state": "Lazio",
            "country": "Italy",
            "base_summary": "Practical wisdom applied to concurrent algorithms.",
        },
        "experiences": [
            {
                "company": "Consortium Inc",
                "position": "Staff Engineer",
                "start_date": "2020-05-01",
                "is_current": True,
                "description": "Orchestrated consensus clusters.",
                "responsibilities": ["Implemented Raft protocol", "Tuned latency"],
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "issue_date": "2021-06-15",
                "credential_url": "https://aws.amazon.com/verification",
            }
        ],
        "achievements": [
            {
                "title": "Best Innovation Award",
                "issuer": "Tech Summit",
                "date": "2022-11-20",
                "description": "Recognized for novel Paxos visualizer.",
            }
        ],
        "section_order": ["experiences", "certifications", "achievements", "summary"],
    }

    patch_res = await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": legacy_payload},
        headers=headers,
    )
    assert patch_res.status_code == 200
    snap = patch_res.json()["content_snapshot"]

    # Assert canonical normalization
    assert snap["schema_version"] == "2.0.0"
    assert snap["basics"]["name"] == "Marcus Aurelius"
    assert snap["basics"]["label"] == "Philosophy & Distributed Systems"
    assert snap["basics"]["location"]["city"] == "Rome"
    assert snap["basics"]["location"]["region"] == "Lazio"
    assert snap["basics"]["location"]["country"] == "Italy"

    # Canonical collections populated from legacy
    assert len(snap["work"]) == 1
    assert snap["work"][0]["name"] == "Consortium Inc"
    assert snap["work"][0]["startDate"] == "2020-05-01"
    assert "Implemented Raft protocol" in snap["work"][0]["highlights"]

    assert len(snap["certificates"]) == 1
    assert snap["certificates"][0]["name"] == "AWS Certified Solutions Architect"
    assert snap["certificates"][0]["issuer"] == "Amazon Web Services"
    assert snap["certificates"][0]["date"] == "2021-06-15"

    assert len(snap["awards"]) == 1
    assert snap["awards"][0]["title"] == "Best Innovation Award"
    assert snap["awards"][0]["awarder"] == "Tech Summit"
    assert snap["awards"][0]["summary"] == "Recognized for novel Paxos visualizer."

    # Presentation section order normalized
    assert snap["presentation"]["section_order"] == ["work", "certificates", "awards", "basics"]

    # Backward compatibility mirrors populated
    assert len(snap["experiences"]) == 1
    assert snap["experiences"][0]["company"] == "Consortium Inc"
    assert len(snap["certifications"]) == 1
    assert len(snap["achievements"]) == 1


@pytest.mark.asyncio
async def test_conflicting_canonical_and_legacy_collections_rejected(async_client: AsyncClient):
    """Test that conflicting non-empty canonical and legacy collections trigger validation rejection (422)."""
    headers = await get_auth_headers(async_client, "cv_conflict@example.com")
    await setup_candidate_profile(async_client, headers)

    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Conflict Testing Version"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]

    # Conflicting work and experiences collections
    conflicting_payload = {
        "work": [
            {"name": "Company Alpha", "position": "Senior Backend"}
        ],
        "experiences": [
            {"company": "Company Beta", "position": "Junior Frontend"}
        ],
    }

    patch_res = await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": conflicting_payload},
        headers=headers,
    )
    assert patch_res.status_code == 422


@pytest.mark.asyncio
async def test_presentation_visibility_and_json_resume_export(async_client: AsyncClient):
    """Test section and item visibility configuration and clean JSON Resume export."""
    headers = await get_auth_headers(async_client, "cv_visibility@example.com")
    await setup_candidate_profile(async_client, headers)

    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Visibility Controlled Version"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]
    snapshot = cv_res.json()["content_snapshot"]

    work_item_id = snapshot["work"][0]["id"]

    # Update presentation: hide the work item, and hide the entire projects section
    snapshot["presentation"]["item_visibility"] = {str(work_item_id): False}
    snapshot["presentation"]["section_visibility"] = {"projects": False, "work": True, "skills": True}

    patch_res = await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": snapshot},
        headers=headers,
    )
    assert patch_res.status_code == 200

    # 1. Export JSON Resume with apply_visibility=True
    export_filtered = await async_client.get(
        f"/api/v1/cv/versions/{cv_id}/json-resume?apply_visibility=true",
        headers=headers,
    )
    assert export_filtered.status_code == 200
    filtered_doc = export_filtered.json()

    assert "$schema" in filtered_doc
    # Work item was hidden
    assert len(filtered_doc["work"]) == 0
    # Projects section was hidden
    assert len(filtered_doc["projects"]) == 0
    # Skills section was visible
    assert len(filtered_doc["skills"]) == 1
    # Check that application-only fields are stripped
    assert "presentation" not in filtered_doc
    assert "extensions" not in filtered_doc
    assert "experiences" not in filtered_doc

    # 2. Export JSON Resume with apply_visibility=False (unfiltered standard export)
    export_unfiltered = await async_client.get(
        f"/api/v1/cv/versions/{cv_id}/json-resume?apply_visibility=false",
        headers=headers,
    )
    assert export_unfiltered.status_code == 200
    unfiltered_doc = export_unfiltered.json()
    assert len(unfiltered_doc["work"]) == 1
    assert len(unfiltered_doc["projects"]) == 1


@pytest.mark.asyncio
async def test_inline_summary_and_bullet_points_overrides_isolation(async_client: AsyncClient):
    """Test that inline summary and highlight overrides update only the version and keep CandidateProfile pristine."""
    headers = await get_auth_headers(async_client, "cv_overrides@example.com")
    await setup_candidate_profile(async_client, headers)

    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Overridden CV Version"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]
    snapshot = cv_res.json()["content_snapshot"]

    # Override summary, headline, and bullet points
    snapshot["basics"]["label"] = "VP of Infrastructure Engineering"
    snapshot["basics"]["professional_headline"] = "VP of Infrastructure Engineering"
    snapshot["basics"]["summary"] = "Driving planetary scale microservice reliability."
    snapshot["basics"]["base_summary"] = "Driving planetary scale microservice reliability."
    snapshot["work"][0]["highlights"] = [
        "Reduced p99 billing latency by 65% across 20 global regions",
        "Orchestrated zero-downtime database failover automation",
    ]

    update_res = await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": snapshot},
        headers=headers,
    )
    assert update_res.status_code == 200
    updated_snap = update_res.json()["content_snapshot"]

    assert updated_snap["basics"]["label"] == "VP of Infrastructure Engineering"
    assert updated_snap["basics"]["summary"] == "Driving planetary scale microservice reliability."
    assert len(updated_snap["work"][0]["highlights"]) == 2
    assert "Reduced p99 billing latency by 65%" in updated_snap["work"][0]["highlights"][0]

    # Verify master profile remains pristine
    master_res = await async_client.get("/api/v1/profile", headers=headers)
    assert master_res.status_code == 200
    master = master_res.json()
    assert master["professional_headline"] == "Lead Systems Architect & Full Stack Engineer"
    assert master["base_summary"] == "Architecting resilient distributed systems and enterprise React web platforms."


@pytest.mark.asyncio
async def test_duplicate_version_preserves_independent_presentation_and_overrides(async_client: AsyncClient):
    """Test duplicating a version clones custom presentation and overrides into an isolated snapshot."""
    headers = await get_auth_headers(async_client, "cv_dup_pres@example.com")
    await setup_candidate_profile(async_client, headers)

    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Source Pitch"},
        headers=headers,
    )
    assert cv_res.status_code == 201
    orig_id = cv_res.json()["id"]
    snapshot = cv_res.json()["content_snapshot"]

    snapshot["presentation"]["section_order"] = ["skills", "work", "projects", "education"]
    snapshot["presentation"]["section_visibility"]["education"] = False
    snapshot["basics"]["summary"] = "Original Pitch Summary"
    snapshot["basics"]["base_summary"] = "Original Pitch Summary"

    await async_client.patch(
        f"/api/v1/cv/versions/{orig_id}",
        json={"content_snapshot": snapshot},
        headers=headers,
    )

    # Duplicate version
    dup_res = await async_client.post(
        f"/api/v1/cv/versions/{orig_id}/duplicate",
        json={"name": "Cloned Pitch"},
        headers=headers,
    )
    assert dup_res.status_code == 201
    dup_data = dup_res.json()
    dup_id = dup_data["id"]

    assert dup_data["content_snapshot"]["presentation"]["section_order"] == ["skills", "work", "projects", "education"]
    assert dup_data["content_snapshot"]["presentation"]["section_visibility"]["education"] is False
    assert dup_data["content_snapshot"]["basics"]["summary"] == "Original Pitch Summary"

    # Modify clone's snapshot
    clone_snap = dup_data["content_snapshot"]
    clone_snap["presentation"]["section_order"] = ["education", "work"]
    clone_snap["basics"]["summary"] = "Cloned Divergent Summary"
    clone_snap["basics"]["base_summary"] = "Cloned Divergent Summary"
    await async_client.patch(
        f"/api/v1/cv/versions/{dup_id}",
        json={"content_snapshot": clone_snap},
        headers=headers,
    )

    # Assert original remains unchanged
    orig_check = await async_client.get(f"/api/v1/cv/versions/{orig_id}", headers=headers)
    assert orig_check.json()["content_snapshot"]["presentation"]["section_order"] == ["skills", "work", "projects", "education"]
    assert orig_check.json()["content_snapshot"]["basics"]["summary"] == "Original Pitch Summary"

