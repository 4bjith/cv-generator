import uuid
import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str = "evidence_tester@example.com") -> dict:
    """Helper to register user and return authorization header."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "Taylor Morgan",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_evidence_crud_and_validation(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "evidence_crud@example.com")

    # 1. Initialize profile
    prof_res = await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Taylor", "last_name": "Morgan"},
        headers=headers,
    )
    assert prof_res.status_code == 201

    # 2. Create evidence item
    ev_payload = {
        "title": "Production Kubernetes Migration Performance Report",
        "description": "Datadog dashboards and Grafana metrics showing 45% latency improvement.",
        "source": "Datadog / Grafana",
        "source_type": "metric_report",
        "url": "https://app.datadoghq.com/dashboard/sample123",
        "notes": "Verified by VP of Engineering during Q3 review.",
        "date": "2024-03",
        "verification_status": "third_party_confirmed",
        "provenance": "user_provided",
    }
    create_res = await async_client.post("/api/v1/profile/evidence", json=ev_payload, headers=headers)
    assert create_res.status_code == 201
    evidence_data = create_res.json()
    assert evidence_data["title"] == ev_payload["title"]
    assert evidence_data["source_type"] == "metric_report"
    assert evidence_data["verification_status"] == "third_party_confirmed"
    assert evidence_data["provenance"] == "user_provided"
    ev_id = evidence_data["id"]

    # 3. List evidence items
    list_res = await async_client.get("/api/v1/profile/evidence", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["id"] == ev_id

    # 4. Get evidence item by ID
    get_res = await async_client.get(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == ev_payload["title"]

    # 5. Update evidence item
    patch_res = await async_client.patch(
        f"/api/v1/profile/evidence/{ev_id}",
        json={"title": "Updated Latency Benchmark", "verification_status": "verified"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated Latency Benchmark"
    assert patch_res.json()["verification_status"] == "verified"

    # 6. Invalid URL validation rejection
    invalid_url_res = await async_client.post(
        "/api/v1/profile/evidence",
        json={
            "title": "Invalid URL Evidence",
            "source": "Manual",
            "url": "ftp://invalid-scheme.com",
        },
        headers=headers,
    )
    assert invalid_url_res.status_code == 422

    # 7. Delete evidence item
    del_res = await async_client.delete(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert del_res.status_code == 204

    # 8. GET deleted evidence -> 404
    get_del = await async_client.get(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert get_del.status_code == 404


@pytest.mark.asyncio
async def test_evidence_associations_with_profile_facts(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "evidence_assoc@example.com")

    # 1. Create Profile
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Jordan", "last_name": "Lee"},
        headers=headers,
    )

    # 2. Add Work Experience
    exp_res = await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Acme Corp",
            "position": "Lead Platform Engineer",
            "start_date": "2022-01",
            "is_current": True,
            "description": "Architected distributed messaging queue handling 100k msg/sec.",
            "metrics": [{"value": 100000, "unit": "msg/sec", "description": "Throughput benchmark"}],
            "provenance": "user_provided",
        },
        headers=headers,
    )
    assert exp_res.status_code == 201
    exp_id = exp_res.json()["id"]

    # 3. Add Project
    proj_res = await async_client.post(
        "/api/v1/profile/projects",
        json={
            "name": "Cloud Observability Agent",
            "role": "Lead Architect",
            "problem": "High memory footprint on edge nodes",
            "solution": "Rewrote telemetry collector in Rust",
            "technologies": ["Rust", "eBPF", "Kubernetes"],
            "live_url": "https://github.com/sample/telemetry",
            "provenance": "imported",
        },
        headers=headers,
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    # 4. Create Evidence and associate with Experience & Project
    ev_res = await async_client.post(
        "/api/v1/profile/evidence",
        json={
            "title": "GitHub Rust Agent Repository & CI Benchmarks",
            "source": "GitHub",
            "source_type": "repository",
            "url": "https://github.com/sample/telemetry",
            "associated_entities": [
                {"entity_type": "experience", "entity_id": exp_id},
                {"entity_type": "project", "entity_id": proj_id},
            ],
        },
        headers=headers,
    )
    assert ev_res.status_code == 201
    ev_id = ev_res.json()["id"]
    assert len(ev_res.json()["associations"]) == 2

    # 5. Fetch complete Profile and verify nested evidence_ids
    prof_res = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    prof_data = prof_res.json()
    assert ev_id in prof_data["experiences"][0]["evidence_ids"]
    assert ev_id in prof_data["projects"][0]["evidence_ids"]
    assert prof_data["projects"][0]["provenance"] == "imported"

    # 6. Disassociate evidence from project
    del_assoc = await async_client.delete(
        f"/api/v1/profile/evidence/{ev_id}/associations/project/{proj_id}",
        headers=headers,
    )
    assert del_assoc.status_code == 204

    # 7. Verify association removal in Profile
    prof_res2 = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_res2.status_code == 200
    assert ev_id not in prof_res2.json()["projects"][0]["evidence_ids"]
    assert ev_id in prof_res2.json()["experiences"][0]["evidence_ids"]


@pytest.mark.asyncio
async def test_skill_relationships_linking_and_sync(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "skills_rel@example.com")

    # 1. Create Profile
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Riley", "last_name": "Reid"},
        headers=headers,
    )

    # 2. Create Experience & Project
    exp_res = await async_client.post(
        "/api/v1/profile/experience",
        json={"company": "FinTech Corp", "position": "Senior Backend Eng", "start_date": "2021-03"},
        headers=headers,
    )
    exp_id = exp_res.json()["id"]

    proj_res = await async_client.post(
        "/api/v1/profile/projects",
        json={"name": "Realtime Trading Engine", "technologies": ["Python", "FastAPI", "Redis"]},
        headers=headers,
    )
    proj_id = proj_res.json()["id"]

    # 3. Create Skill
    skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "FastAPI", "category": "framework", "proficiency": "expert"},
        headers=headers,
    )
    assert skill_res.status_code == 201
    skill_id = skill_res.json()["id"]
    assert len(skill_res.json()["experience_ids"]) == 0

    # 4. Link Skill to Experience & Project via granular endpoints
    link_exp = await async_client.post(
        f"/api/v1/profile/skills/{skill_id}/experiences/{exp_id}",
        headers=headers,
    )
    assert link_exp.status_code == 204

    link_proj = await async_client.post(
        f"/api/v1/profile/skills/{skill_id}/projects/{proj_id}",
        headers=headers,
    )
    assert link_proj.status_code == 204

    # 5. Verify GET /api/v1/profile reflects linked relationships
    prof_res = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    skill_item = next(s for s in prof_res.json()["skills"] if s["id"] == skill_id)
    assert exp_id in skill_item["experience_ids"]
    assert proj_id in skill_item["project_ids"]

    # 6. Test batch relationship sync PUT endpoint
    sync_res = await async_client.put(
        f"/api/v1/profile/skills/{skill_id}/relationships",
        json={
            "experience_ids": [exp_id],
            "project_ids": [],  # unlink project
        },
        headers=headers,
    )
    assert sync_res.status_code == 200
    assert exp_id in sync_res.json()["experience_ids"]
    assert len(sync_res.json()["project_ids"]) == 0


@pytest.mark.asyncio
async def test_profile_quality_scoring_and_recommendations(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "quality_score@example.com")

    # 1. Base profile
    await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Devon",
            "last_name": "Vance",
            "professional_headline": "Full-Stack Engineer",
            "email": "devon@example.com",
            "primary_title": "Full-Stack Engineer",
            "career_level": "mid",
            "base_summary": "Passionate full stack developer with experience in React, Python, and PostgreSQL.",
        },
        headers=headers,
    )

    # 2. Check initial strength & quality breakdown
    str_res1 = await async_client.get("/api/v1/profile/strength", headers=headers)
    assert str_res1.status_code == 200
    data1 = str_res1.json()
    assert "quality" in data1
    assert data1["quality"]["score"] >= 0
    assert len(data1["quality"]["recommendations"]) > 0

    # 3. Add Experience with metrics
    exp_res = await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "ScaleTech Systems",
            "position": "Senior Backend Developer",
            "start_date": "2021-01",
            "is_current": True,
            "description": "Architected low-latency microservices handling millions of events daily.",
            "responsibilities": ["Designed event streaming pipelines", "Managed Redis cache tiers"],
            "technologies": ["Python", "Redis", "Kafka", "PostgreSQL"],
            "metrics": [{"value": 40, "unit": "%", "description": "Latency reduction"}],
        },
        headers=headers,
    )
    exp_id = exp_res.json()["id"]

    # 4. Add Project
    proj_res = await async_client.post(
        "/api/v1/profile/projects",
        json={
            "name": "Event Gateway",
            "role": "Lead Developer",
            "problem": "Handling spike traffic during flash sales",
            "solution": "Implemented token-bucket rate limiting and async worker pools",
            "architecture": "Event-driven distributed architecture using Celery and Redis",
            "technologies": ["Python", "FastAPI", "Redis"],
            "live_url": "https://gateway.example.com",
        },
        headers=headers,
    )
    proj_id = proj_res.json()["id"]

    # 5. Add Evidence supporting the Experience & Project
    await async_client.post(
        "/api/v1/profile/evidence",
        json={
            "title": "ScaleTech Performance Benchmark Metrics",
            "source": "Grafana Dashboards",
            "source_type": "metric_report",
            "url": "https://metrics.scaletech.internal/dashboard/123",
            "associated_entities": [
                {"entity_type": "experience", "entity_id": exp_id},
                {"entity_type": "project", "entity_id": proj_id},
            ],
        },
        headers=headers,
    )

    # 6. Add Skill linked to Experience
    skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={
            "name": "Redis",
            "category": "database",
            "proficiency": "advanced",
            "experience_ids": [exp_id],
            "project_ids": [proj_id],
        },
        headers=headers,
    )
    assert skill_res.status_code == 201

    # 7. Check improved quality breakdown
    str_res2 = await async_client.get("/api/v1/profile/strength", headers=headers)
    assert str_res2.status_code == 200
    data2 = str_res2.json()
    assert data2["quality"]["evidence_coverage"] > data1["quality"]["evidence_coverage"]
    assert data2["quality"]["skill_validation"] > data1["quality"]["skill_validation"]
    assert data2["quality"]["experience_quality"] > 50
    assert data2["quality"]["score"] > data1["quality"]["score"]


@pytest.mark.asyncio
async def test_cross_user_isolation_evidence_and_skill_links(async_client: AsyncClient):
    # Setup User A
    headers_a = await get_auth_headers(async_client, "user_alpha@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Alpha"}, headers=headers_a)
    exp_a = await async_client.post(
        "/api/v1/profile/experience",
        json={"company": "Alpha Corp", "position": "Developer", "start_date": "2020-01"},
        headers=headers_a,
    )
    exp_a_id = exp_a.json()["id"]

    ev_a = await async_client.post(
        "/api/v1/profile/evidence",
        json={"title": "Alpha Evidence", "source": "Internal", "source_type": "document"},
        headers=headers_a,
    )
    ev_a_id = ev_a.json()["id"]

    skill_a = await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Rust", "category": "programming_language"},
        headers=headers_a,
    )
    skill_a_id = skill_a.json()["id"]

    # Setup User B
    headers_b = await get_auth_headers(async_client, "user_bravo@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Bravo"}, headers=headers_b)
    exp_b = await async_client.post(
        "/api/v1/profile/experience",
        json={"company": "Bravo Corp", "position": "Engineer", "start_date": "2021-01"},
        headers=headers_b,
    )
    exp_b_id = exp_b.json()["id"]

    # 1. User B cannot read User A's evidence
    get_other_ev = await async_client.get(f"/api/v1/profile/evidence/{ev_a_id}", headers=headers_b)
    assert get_other_ev.status_code == 404

    # 2. User B cannot delete User A's evidence
    del_other_ev = await async_client.delete(f"/api/v1/profile/evidence/{ev_a_id}", headers=headers_b)
    assert del_other_ev.status_code == 404

    # 3. User B cannot associate User B's evidence with User A's experience
    ev_b = await async_client.post(
        "/api/v1/profile/evidence",
        json={"title": "Bravo Evidence", "source": "Public Repo"},
        headers=headers_b,
    )
    ev_b_id = ev_b.json()["id"]

    hijack_assoc = await async_client.post(
        f"/api/v1/profile/evidence/{ev_b_id}/associations",
        json={"entity_type": "experience", "entity_id": exp_a_id},
        headers=headers_b,
    )
    assert hijack_assoc.status_code == 404

    # 4. User B cannot link skill to User A's experience
    skill_b = await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Go", "category": "programming_language"},
        headers=headers_b,
    )
    skill_b_id = skill_b.json()["id"]

    link_hijack = await async_client.post(
        f"/api/v1/profile/skills/{skill_b_id}/experiences/{exp_a_id}",
        headers=headers_b,
    )
    assert link_hijack.status_code == 404

    # 5. User B cannot link User A's skill to User B's experience
    skill_hijack = await async_client.post(
        f"/api/v1/profile/skills/{skill_a_id}/experiences/{exp_b_id}",
        headers=headers_b,
    )
    assert skill_hijack.status_code == 404

    # 6. User B cannot link User B's skill to User A's project
    proj_a = await async_client.post(
        "/api/v1/profile/projects",
        json={"name": "Alpha Project"},
        headers=headers_a,
    )
    proj_a_id = proj_a.json()["id"]

    link_proj_hijack = await async_client.post(
        f"/api/v1/profile/skills/{skill_b_id}/projects/{proj_a_id}",
        headers=headers_b,
    )
    assert link_proj_hijack.status_code == 404

    # 7. User B cannot unlink User A's skill from User A's experience
    unlink_hijack = await async_client.delete(
        f"/api/v1/profile/skills/{skill_a_id}/experiences/{exp_a_id}",
        headers=headers_b,
    )
    assert unlink_hijack.status_code == 404


@pytest.mark.asyncio
async def test_cascade_deletion_and_no_orphaned_associations(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "cascade_test@example.com")

    # 1. Create Profile
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Casey", "last_name": "Jordan"},
        headers=headers,
    )

    # 2. Add Work Experience and Project
    exp_res = await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Nexus Corp",
            "position": "Infrastructure Lead",
            "start_date": "2020-01",
            "is_current": False,
            "end_date": "2022-01",
        },
        headers=headers,
    )
    exp_id = exp_res.json()["id"]

    proj_res = await async_client.post(
        "/api/v1/profile/projects",
        json={"name": "Nexus Edge CDN", "technologies": ["Go", "Docker"]},
        headers=headers,
    )
    proj_id = proj_res.json()["id"]

    # 3. Add Skill linked to Experience and Project
    skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={
            "name": "Docker",
            "category": "devops",
            "experience_ids": [exp_id],
            "project_ids": [proj_id],
        },
        headers=headers,
    )
    skill_id = skill_res.json()["id"]

    # 4. Add Evidence item associated with Experience and Project
    ev_res = await async_client.post(
        "/api/v1/profile/evidence",
        json={
            "title": "Nexus CDN Benchmark Whitepaper",
            "source": "Nexus Engineering Blog",
            "source_type": "document",
            "associated_entities": [
                {"entity_type": "experience", "entity_id": exp_id},
                {"entity_type": "project", "entity_id": proj_id},
            ],
        },
        headers=headers,
    )
    ev_id = ev_res.json()["id"]

    # Verify initial associations in evidence and skill
    ev_check = await async_client.get(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert len(ev_check.json()["associations"]) == 2

    # 5. Delete Work Experience
    del_exp_res = await async_client.delete(f"/api/v1/profile/experience/{exp_id}", headers=headers)
    assert del_exp_res.status_code == 204

    # 6. Verify evidence association was automatically cleaned up (only project remains)
    ev_after_exp = await async_client.get(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert len(ev_after_exp.json()["associations"]) == 1
    assert ev_after_exp.json()["associations"][0]["entity_type"] == "project"

    # 7. Verify skill relational links automatically cleaned up (experience_ids empty)
    prof_after_exp = await async_client.get("/api/v1/profile", headers=headers)
    skill_item = next(s for s in prof_after_exp.json()["skills"] if s["id"] == skill_id)
    assert exp_id not in skill_item["experience_ids"]
    assert proj_id in skill_item["project_ids"]

    # 8. Delete Project
    del_proj_res = await async_client.delete(f"/api/v1/profile/projects/{proj_id}", headers=headers)
    assert del_proj_res.status_code == 204

    # 9. Verify evidence item has 0 associations now, without any errors or orphaned records
    ev_after_proj = await async_client.get(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert len(ev_after_proj.json()["associations"]) == 0

    # 10. Delete Evidence item
    del_ev_res = await async_client.delete(f"/api/v1/profile/evidence/{ev_id}", headers=headers)
    assert del_ev_res.status_code == 204

    # Verify skill still intact and valid
    prof_final = await async_client.get("/api/v1/profile", headers=headers)
    assert len(prof_final.json()["skills"]) == 1


@pytest.mark.asyncio
async def test_provenance_distinction_and_ai_protection(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "provenance_test@example.com")

    # 1. Create Profile
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Sam", "last_name": "Rivera"},
        headers=headers,
    )

    # 2. Add user-provided experience
    exp_res = await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Original Corp",
            "position": "Software Engineer",
            "start_date": "2021-01",
            "provenance": "user_provided",
        },
        headers=headers,
    )
    assert exp_res.status_code == 201
    assert exp_res.json()["provenance"] == "user_provided"

    # 3. Add AI-enhanced project
    proj_res = await async_client.post(
        "/api/v1/profile/projects",
        json={
            "name": "AI Assistant Service",
            "problem": "Manual customer triage",
            "solution": "Automated intent routing",
            "provenance": "ai_enhanced",
        },
        headers=headers,
    )
    assert proj_res.status_code == 201
    assert proj_res.json()["provenance"] == "ai_enhanced"

    # 4. Add imported skill
    skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={
            "name": "Kubernetes",
            "category": "devops",
            "provenance": "imported",
        },
        headers=headers,
    )
    assert skill_res.status_code == 201
    assert skill_res.json()["provenance"] == "imported"

    # 5. Add AI-generated evidence
    ev_res = await async_client.post(
        "/api/v1/profile/evidence",
        json={
            "title": "Automated Benchmark Summary",
            "source": "AI Metric Aggregator",
            "provenance": "ai_generated",
        },
        headers=headers,
    )
    assert ev_res.status_code == 201
    assert ev_res.json()["provenance"] == "ai_generated"

    # 6. Verify full profile preserves each provenance tag accurately
    prof_res = await async_client.get("/api/v1/profile", headers=headers)
    data = prof_res.json()
    assert data["experiences"][0]["provenance"] == "user_provided"
    assert data["projects"][0]["provenance"] == "ai_enhanced"
    assert data["skills"][0]["provenance"] == "imported"
    assert data["evidence_items"][0]["provenance"] == "ai_generated"
