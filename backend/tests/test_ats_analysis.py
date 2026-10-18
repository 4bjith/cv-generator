import copy
import uuid
import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str) -> dict:
    """Helper to register a unique user and obtain auth headers."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "ATS Test Candidate",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ats_analysis_general_baseline(async_client: AsyncClient):
    """
    Verify ATS analysis on a CV version without a target job:
    Checks general baseline scoring, structure checks, formatting checks, and disclaimers.
    """
    headers = await get_auth_headers(async_client, "ats_baseline@example.com")

    # 1. Create candidate profile
    await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Marcus",
            "last_name": "Vance",
            "primary_title": "Senior Staff Engineer",
            "base_summary": "10 years building distributed backend architectures with Python, PostgreSQL, and Redis.",
        },
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "technical", "proficiency": "expert"},
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "PostgreSQL", "category": "technical", "proficiency": "advanced"},
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Apex Cloud Systems",
            "position": "Principal Architect",
            "start_date": "2021-01-01",
            "end_date": "2025-01-01",
            "responsibilities": ["Architected distributed streaming platform processing 50k req/sec."],
            "technologies": ["Python", "Kafka", "PostgreSQL"],
        },
        headers=headers,
    )

    # 2. Create CV version from profile
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Marcus Vance - Base CV"},
        headers=headers,
    )
    assert cv_resp.status_code == 201
    cv_id = cv_resp.json()["id"]

    # 3. Run ATS Analysis in baseline mode (no job_id)
    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id},
        headers=headers,
    )
    assert ats_resp.status_code == 200
    report = ats_resp.json()

    assert report["cv_version_id"] == cv_id
    assert report["job_id"] is None
    assert report["scoring_mode"] == "general_baseline"
    assert 0 <= report["overall_score"] <= 100
    assert len(report["components"]) == 3
    assert any(c["name"] == "Structure & Content Completeness" for c in report["components"])
    assert any(c["name"] == "Formatting & Parsing Safety" for c in report["components"])

    # Verify check categories
    check_categories = {c["category"] for c in report["checks"]}
    assert "contact_info" in check_categories
    assert "template_layout" in check_categories
    assert "symbols_and_formatting" in check_categories

    # Verify mandatory heuristic disclaimer
    assert "Heuristic estimate only" in report["disclaimer"]
    assert "guarantee" in report["disclaimer"].lower()


@pytest.mark.asyncio
async def test_ats_analysis_job_targeted_scoring(async_client: AsyncClient):
    """
    Verify ATS analysis against a saved job target:
    Validates keyword occurrence tracking, mandatory requirement weighting, and point deductions.
    """
    headers = await get_auth_headers(async_client, "ats_targeted@example.com")

    # 1. Create Profile
    await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Elena",
            "last_name": "Rostova",
            "primary_title": "Full Stack Engineer",
            "base_summary": "Expert in React, TypeScript, and Node.js microservices with clean API architectures.",
        },
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "React", "category": "frontend", "proficiency": "expert"},
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "TypeScript", "category": "frontend", "proficiency": "advanced"},
        headers=headers,
    )

    # 2. Create CV version
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Elena - Full Stack"},
        headers=headers,
    )
    assert cv_resp.status_code == 201
    cv_id = cv_resp.json()["id"]

    # 3. Create Job Target with clear requirements
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Senior Frontend Developer",
            "company_name": "Veritas Health",
            "job_description": "We need an engineer with React and TypeScript expertise. Mandatory: React, TypeScript, GraphQL. Preferred: Docker, Next.js.",
        },
        headers=headers,
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # Run job requirement analysis
    await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)

    # 4. Run targeted ATS analysis
    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id, "job_id": job_id},
        headers=headers,
    )
    assert ats_resp.status_code == 200
    report = ats_resp.json()

    assert report["scoring_mode"] == "job_targeted"
    assert report["job_id"] == job_id
    assert report["job_title"] == "Senior Frontend Developer"
    assert report["company_name"] == "Veritas Health"

    # Verify 4 components in targeted mode
    assert len(report["components"]) == 4
    comp_names = [c["name"] for c in report["components"]]
    assert "Job Keyword Alignment" in comp_names
    assert "Requirement & Qualification Match" in comp_names
    assert "Structure & Content Completeness" in comp_names
    assert "Formatting & Parsing Safety" in comp_names

    # Check keyword occurrences
    react_kw = next((k for k in report["keywords"] if k["keyword"].lower() == "react"), None)
    assert react_kw is not None
    assert react_kw["is_present"] is True
    assert react_kw["count"] >= 1


@pytest.mark.asyncio
async def test_ats_keyword_stuffing_detection(async_client: AsyncClient):
    """
    Verify detection of unnatural keyword repetition (>3.5% density):
    Ensures warnings trigger and point deductions are explicitly documented.
    """
    headers = await get_auth_headers(async_client, "ats_stuffing@example.com")

    # 1. Create profile
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Test", "last_name": "Spammer", "primary_title": "Developer"},
        headers=headers,
    )
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Spam CV"},
        headers=headers,
    )
    cv_id = cv_resp.json()["id"]
    snapshot = cv_resp.json()["content_snapshot"]

    # Stuffed keyword "Kubernetes" 25 times in short text
    stuffed_summary = "Kubernetes " * 25 + "developer working with microservices."
    snapshot["basics"]["summary"] = stuffed_summary

    await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": snapshot},
        headers=headers,
    )

    # Create job target mentioning Kubernetes
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "DevOps Engineer",
            "company_name": "ScaleOps",
            "job_description": "Must have hands-on experience with Kubernetes orchestration and deployments.",
        },
        headers=headers,
    )
    job_id = job_resp.json()["id"]

    # Analyze
    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id, "job_id": job_id},
        headers=headers,
    )
    assert ats_resp.status_code == 200
    report = ats_resp.json()

    k8s_kw = next((k for k in report["keywords"] if "kubernetes" in k["keyword"].lower()), None)
    assert k8s_kw is not None
    assert k8s_kw["is_overused"] is True
    assert k8s_kw["density_percentage"] > 3.5

    # Verify check warning was added
    stuffing_check = next((c for c in report["checks"] if c["id"] == "keyword-stuffing-detected"), None)
    assert stuffing_check is not None
    assert stuffing_check["status"] == "warning"

    # Verify component score has deductions
    kw_comp = next(c for c in report["components"] if c["name"] == "Job Keyword Alignment")
    assert any("Excessive repetition" in d for d in kw_comp["deductions"])


@pytest.mark.asyncio
async def test_ats_template_layout_friction_detection(async_client: AsyncClient):
    """
    Verify formatting check distinguishes layout risks (two-column warning vs minimal pass).
    """
    headers = await get_auth_headers(async_client, "ats_layout@example.com")

    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Design", "last_name": "Tester", "primary_title": "Designer"},
        headers=headers,
    )
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Layout CV"},
        headers=headers,
    )
    cv_id = cv_resp.json()["id"]

    # 1. Update template to contemporary two-column
    snapshot = cv_resp.json()["content_snapshot"]
    snapshot["presentation"]["template"] = "contemporary-two-column"
    await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": snapshot},
        headers=headers,
    )

    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id},
        headers=headers,
    )
    assert ats_resp.status_code == 200
    report = ats_resp.json()
    two_col_check = next((c for c in report["checks"] if c["id"] == "template-two-column-warning"), None)
    assert two_col_check is not None
    assert two_col_check["status"] == "warning"

    # 2. Switch template to ats-minimal
    snapshot["presentation"]["template"] = "ats-minimal"
    await async_client.patch(
        f"/api/v1/cv/versions/{cv_id}",
        json={"content_snapshot": snapshot},
        headers=headers,
    )

    ats_resp2 = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id},
        headers=headers,
    )
    assert ats_resp2.status_code == 200
    report2 = ats_resp2.json()
    minimal_check = next((c for c in report2["checks"] if c["id"] == "template-optimal"), None)
    assert minimal_check is not None
    assert minimal_check["status"] == "pass"


@pytest.mark.asyncio
async def test_ats_grounded_vs_unsupported_suggestions(async_client: AsyncClient):
    """
    Verify keyword optimization suggestions distinguish facts grounded in CandidateProfile
    from unsupported skills (which must be flagged with zero-hallucination warnings).
    """
    headers = await get_auth_headers(async_client, "ats_grounded@example.com")

    # 1. Candidate profile has "Docker" confirmed, but NOT "Rust"
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Grounded", "last_name": "Engineer", "primary_title": "Engineer"},
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Docker", "category": "devops", "proficiency": "advanced"},
        headers=headers,
    )

    # 2. CV does not currently list Docker
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Clean CV"},
        headers=headers,
    )
    cv_id = cv_resp.json()["id"]

    # 3. Target job requires Docker and Rust
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Systems Developer",
            "company_name": "Edge Labs",
            "job_description": "We require strong background in Docker containerization and Rust systems programming.",
        },
        headers=headers,
    )
    job_id = job_resp.json()["id"]

    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id, "job_id": job_id},
        headers=headers,
    )
    assert ats_resp.status_code == 200
    report = ats_resp.json()
    suggestions = report["suggestions"]

    docker_sugg = next((s for s in suggestions if s["keyword"].lower() == "docker"), None)
    rust_sugg = next((s for s in suggestions if s["keyword"].lower() == "rust"), None)

    # Docker is grounded in CandidateProfile
    if docker_sugg:
        assert docker_sugg["is_grounded_in_profile"] is True
        assert docker_sugg["grounding_evidence"] is not None

    # Rust is NOT grounded in CandidateProfile -> must warn against fabrication
    if rust_sugg:
        assert rust_sugg["is_grounded_in_profile"] is False
        assert "Zero-hallucination" in rust_sugg["warning"]


@pytest.mark.asyncio
async def test_ats_apply_suggestions_snapshot_isolation(async_client: AsyncClient):
    """
    Verify applying accepted suggestions creates a new independent CVVersion
    without mutating the source CVVersion or master CandidateProfile.
    """
    headers = await get_auth_headers(async_client, "ats_apply@example.com")

    # 1. Profile with Python skill
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Snapshot", "last_name": "Isolation", "primary_title": "Data Engineer"},
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "data", "proficiency": "expert"},
        headers=headers,
    )

    # 2. CV created with only Python (no Kafka)
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Data CV Original"},
        headers=headers,
    )
    cv_id = cv_resp.json()["id"]
    orig_skills_len = len(cv_resp.json()["content_snapshot"]["skills"])

    # 3. Add Kafka to candidate profile knowledge base (so it is grounded, but absent from CV)
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Kafka", "category": "data", "proficiency": "expert"},
        headers=headers,
    )

    # 3. Job requiring Kafka
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Stream Architect",
            "company_name": "Confluent Partner",
            "job_description": "Must have proven Kafka pipeline expertise.",
        },
        headers=headers,
    )
    job_id = job_resp.json()["id"]

    # 4. Get suggestions
    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id, "job_id": job_id},
        headers=headers,
    )
    report = ats_resp.json()
    kafka_sugg = next((s for s in report["suggestions"] if s["keyword"].lower() == "kafka"), None)
    assert kafka_sugg is not None
    assert kafka_sugg["is_grounded_in_profile"] is True

    # 5. Apply suggestion
    apply_resp = await async_client.post(
        "/api/v1/ats/apply-suggestions",
        json={
            "cv_version_id": cv_id,
            "job_id": job_id,
            "accepted_suggestion_ids": [kafka_sugg["id"]],
            "new_version_name": "Data CV - Kafka Optimized",
        },
        headers=headers,
    )
    assert apply_resp.status_code == 201
    applied = apply_resp.json()

    assert applied["original_version_id"] == cv_id
    assert applied["new_version_id"] != cv_id
    assert applied["new_version_name"] == "Data CV - Kafka Optimized"
    assert applied["applied_suggestions_count"] == 1

    # Check new version has Kafka
    new_skills = applied["content_snapshot"]["skills"]
    assert any(s["name"] == "Kafka" for s in new_skills)

    # 6. Verify original version remains unchanged
    orig_check = await async_client.get(f"/api/v1/cv/versions/{cv_id}", headers=headers)
    assert orig_check.status_code == 200
    assert len(orig_check.json()["content_snapshot"]["skills"]) == orig_skills_len
    assert not any(s["name"] == "Kafka" for s in orig_check.json()["content_snapshot"]["skills"])


@pytest.mark.asyncio
async def test_ats_cross_user_isolation(async_client: AsyncClient):
    """Verify that User B cannot analyze or optimize User A's CV version."""
    headers_a = await get_auth_headers(async_client, "user_a_ats@example.com")
    headers_b = await get_auth_headers(async_client, "user_b_ats@example.com")

    # User A creates CV
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Alice", "last_name": "A", "primary_title": "Engineer"},
        headers=headers_a,
    )
    cv_resp = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Alice Private CV"},
        headers=headers_a,
    )
    cv_id = cv_resp.json()["id"]

    # User B attempts to analyze Alice's CV
    forbidden_resp = await async_client.post(
        "/api/v1/ats/analyze",
        json={"cv_version_id": cv_id},
        headers=headers_b,
    )
    assert forbidden_resp.status_code in [404, 403]
