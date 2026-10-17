import uuid
import pytest
from httpx import AsyncClient


async def get_auth_headers(client: AsyncClient, email: str = "intelligence_user@example.com") -> dict:
    """Helper fixture to register a user and obtain authorization header."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "Job Intelligence Candidate",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


SAMPLE_JOB_DESCRIPTION = """
We are looking for a Senior Full-Stack Engineer to join our Platform team.

Responsibilities:
- Build and maintain high-performance microservices using FastAPI and PostgreSQL.
- Design responsive, accessible user interfaces with Next.js, React, and TypeScript.
- Collaborate with product designers and engineers across the full software lifecycle.

Minimum Qualifications:
- 5+ years of software engineering experience.
- Proficiency in Python, TypeScript, and SQL databases (PostgreSQL preferred).
- Hands-on experience with Docker, CI/CD pipelines, and cloud services (AWS or GCP).
- Bachelor's degree in Computer Science or equivalent practical experience.

Preferred Qualifications:
- Experience with GraphQL and Redis caching.
- Familiarity with AI tools, LLM providers, and vector databases.
- AWS Certified Solutions Architect.

Requirements & Constraints:
- Must be authorized to work in the United States without visa sponsorship.
"""


@pytest.mark.asyncio
async def test_job_target_crud_with_employment_type_and_validation(async_client: AsyncClient):
    """Test job target creation, retrieval, and updating with employment type and validation."""
    headers = await get_auth_headers(async_client, "job_crud_emp@example.com")

    # 1. Validation: reject empty title or whitespace-only job description
    bad_payload = {
        "title": "   ",
        "company_name": "Acme Corp",
        "job_description": "   ",
    }
    res_bad = await async_client.post("/api/v1/jobs", json=bad_payload, headers=headers)
    assert res_bad.status_code == 422

    # 2. Valid creation with employment_type
    payload = {
        "title": "Senior Full-Stack Engineer",
        "company_name": "Stripe",
        "location": "San Francisco, CA (Hybrid)",
        "employment_type": "Full-time",
        "job_description": SAMPLE_JOB_DESCRIPTION,
        "source_url": "https://stripe.com/jobs/senior-fs",
        "user_notes": "Important target role.",
        "status": "saved",
    }
    create_res = await async_client.post("/api/v1/jobs", json=payload, headers=headers)
    assert create_res.status_code == 201
    job_data = create_res.json()
    assert job_data["title"] == "Senior Full-Stack Engineer"
    assert job_data["employment_type"] == "Full-time"
    assert job_data["status"] == "saved"
    job_id = job_data["id"]

    # 3. Update employment_type
    update_res = await async_client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"employment_type": "Contract", "location": "Remote"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["employment_type"] == "Contract"
    assert update_res.json()["location"] == "Remote"


@pytest.mark.asyncio
async def test_requirement_extraction_mandatory_vs_preferred(async_client: AsyncClient):
    """Verify structured requirement extraction classifies mandatory vs preferred correctly."""
    headers = await get_auth_headers(async_client, "extractor_test@example.com")

    # Ad-hoc extraction endpoint test
    extract_payload = {
        "job_description": SAMPLE_JOB_DESCRIPTION,
        "title": "Senior Full-Stack Engineer",
        "company_name": "Platform Co",
    }
    res = await async_client.post("/api/v1/jobs/extract", json=extract_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["seniority_level"] == "Senior"
    assert len(data["requirements"]) > 0
    assert "Fastapi" in data["extracted_keywords"] or "Postgresql" in data["extracted_keywords"] or "Python" in data["extracted_keywords"]

    # Verify canonical requirement structure
    reqs = data["requirements"]
    categories = {r["category"] for r in reqs}
    assert "responsibilities" in categories or "technologies" in categories or "skills" in categories

    # Verify mandatory vs preferred separation
    mandatory_reqs = [r for r in reqs if r["is_mandatory"]]
    preferred_reqs = [r for r in reqs if not r["is_mandatory"]]

    assert len(mandatory_reqs) > 0
    assert len(preferred_reqs) > 0

    # Minimum qualifications (e.g. 5+ years, Python/TypeScript) should be mandatory
    assert any("5+" in r["requirement"] or "years" in r["requirement"].lower() for r in mandatory_reqs)
    # Preferred qualifications (e.g. GraphQL, AWS Certified) should be preferred
    assert any("graphql" in r["requirement"].lower() or "aws certified" in r["requirement"].lower() for r in preferred_reqs)


@pytest.mark.asyncio
async def test_evidence_grounded_matching_and_traceability(async_client: AsyncClient):
    """
    Test evidence-grounded matching against candidate profile:
    - Supported match with evidence traceability
    - Unverified match (claim in profile but no evidence)
    - Missing qualification (gap_type: absent_from_profile)
    - Immutability of candidate profile
    """
    headers = await get_auth_headers(async_client, "grounded_matching@example.com")

    # 1. Create Candidate Profile
    prof_res = await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Elena",
            "last_name": "Rostova",
            "primary_title": "Senior Backend Architect",
            "summary": "Full-stack engineer with 6 years experience in Python and PostgreSQL.",
        },
        headers=headers,
    )
    assert prof_res.status_code == 201

    # 2. Add a verified skill (Python) backed by EvidenceItem
    skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={
            "name": "Python",
            "category": "technical",
            "proficiency": "expert",
            "years_of_experience": 6.0,
        },
        headers=headers,
    )
    assert skill_res.status_code == 201
    skill_id = skill_res.json()["id"]

    # Attach evidence item to the skill
    ev_res = await async_client.post(
        "/api/v1/profile/evidence",
        json={
            "title": "Open Source FastAPI Microservice",
            "source": "GitHub",
            "source_type": "link",
            "url": "https://github.com/elena/fastapi-microservice",
            "verification_status": "verified",
            "associated_entities": [{"entity_type": "skill", "entity_id": skill_id}],
        },
        headers=headers,
    )
    assert ev_res.status_code == 201

    # 3. Add an unverified skill (Docker - claimed without evidence item)
    unverified_skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={
            "name": "Docker",
            "category": "tools",
            "proficiency": "intermediate",
            "years_of_experience": 3.0,
        },
        headers=headers,
    )
    assert unverified_skill_res.status_code == 201

    # 4. Add Work Experience satisfying 5+ years experience
    exp_res = await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "ScaleTech Systems",
            "position": "Senior Backend Engineer",
            "start_date": "2018-01-01",
            "end_date": "2024-01-01",
            "is_current": False,
            "description": "Led backend architecture using Python, FastAPI, and PostgreSQL.",
            "responsibilities": ["Designed and maintained high-performance microservices using FastAPI and PostgreSQL."],
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
        },
        headers=headers,
    )
    assert exp_res.status_code == 201

    # 5. Create Job Target
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Senior Full-Stack Engineer",
            "company_name": "Lattice Systems",
            "job_description": SAMPLE_JOB_DESCRIPTION,
            "status": "saved",
        },
        headers=headers,
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 6. Run Job Analysis (Analyze endpoint)
    analyze_res = await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)
    assert analyze_res.status_code == 200
    analysis_data = analyze_res.json()

    assert analysis_data["job_id"] == job_id
    analysis = analysis_data["analysis"]
    requirements = analysis["requirements"]
    summary = analysis["keyword_summary"]

    assert summary["total_requirements"] > 0
    assert summary["supported_count"] >= 1
    assert summary["coverage_percentage"] > 0.0

    # Verify Supported Match with Traceability
    supported_items = [r for r in requirements if r["candidate_match_status"] == "supported"]
    assert len(supported_items) > 0
    python_matches = [r for r in supported_items if "python" in r["requirement"].lower() or r.get("matched_entity_name") == "Python"]
    assert len(python_matches) > 0
    py_match = python_matches[0]
    assert len(py_match["evidence_items"]) > 0
    assert py_match["evidence_items"][0]["title"] == "Open Source FastAPI Microservice"
    assert py_match["confidence_score"] >= 0.85
    assert "Directly verified" in py_match["reasoning"]

    # Verify Unverified Match (claimed Docker without evidence)
    unverified_items = [r for r in requirements if r["candidate_match_status"] == "unverified"]
    docker_matches = [r for r in unverified_items if "docker" in r["requirement"].lower() or r.get("matched_entity_name") == "Docker"]
    if docker_matches:
        doc_match = docker_matches[0]
        assert doc_match["gap_type"] == "unverified_claim"
        assert len(doc_match["evidence_items"]) == 0
        assert "no supporting evidence" in doc_match["reasoning"].lower()

    # Verify Missing Qualification (e.g. AWS Certified Solutions Architect or GraphQL)
    missing_items = [r for r in requirements if r["candidate_match_status"] == "missing"]
    assert len(missing_items) > 0
    aws_cert_matches = [r for r in missing_items if "aws certified" in r["requirement"].lower()]
    if aws_cert_matches:
        assert aws_cert_matches[0]["gap_type"] in {"absent_from_profile", "skill_gap"}

    # 7. Verify Retrieval via GET /api/v1/jobs/{job_id}/analysis
    get_analysis_res = await async_client.get(f"/api/v1/jobs/{job_id}/analysis", headers=headers)
    assert get_analysis_res.status_code == 200
    retrieved_analysis = get_analysis_res.json()["analysis"]
    assert retrieved_analysis["job_id"] == job_id
    assert len(retrieved_analysis["requirements"]) == len(requirements)

    # 8. Profile Immutability check: ensure CandidateProfile facts were not mutated
    prof_check = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_check.status_code == 200
    p_data = prof_check.json()
    assert p_data["first_name"] == "Elena"
    assert p_data["last_name"] == "Rostova"
    assert len(p_data["skills"]) == 2


@pytest.mark.asyncio
async def test_job_target_associated_cv_versions(async_client: AsyncClient):
    """Verify association between job target and CV versions without mutating master profile."""
    headers = await get_auth_headers(async_client, "job_versions_test@example.com")

    # 1. Create profile
    await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Marcus",
            "last_name": "Vance",
            "primary_title": "Full-Stack Engineer",
        },
        headers=headers,
    )

    # 2. Create job target
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Staff Infrastructure Engineer",
            "company_name": "Cloudflare",
            "job_description": "We need a staff engineer to build distributed systems.",
            "status": "saved",
        },
        headers=headers,
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # 3. Create CV version explicitly linked to this job target
    cv_res = await async_client.post(
        "/api/v1/cv/versions",
        json={
            "name": "Cloudflare Staff Application CV",
            "job_target_id": job_id,
        },
        headers=headers,
    )
    assert cv_res.status_code == 201
    cv_id = cv_res.json()["id"]

    # 4. Query /api/v1/jobs/{job_id}/versions
    versions_res = await async_client.get(f"/api/v1/jobs/{job_id}/versions", headers=headers)
    assert versions_res.status_code == 200
    versions_data = versions_res.json()
    assert versions_data["total"] == 1
    assert versions_data["items"][0]["id"] == cv_id
    assert versions_data["items"][0]["job_target_id"] == job_id
    assert versions_data["items"][0]["name"] == "Cloudflare Staff Application CV"


@pytest.mark.asyncio
async def test_cross_user_job_target_and_analysis_isolation(async_client: AsyncClient):
    """Ensure User B cannot analyze or view User A's job targets or analysis results."""
    user_a_headers = await get_auth_headers(async_client, "user_a_jobs@example.com")
    user_b_headers = await get_auth_headers(async_client, "user_b_jobs@example.com")

    # User A creates a job target
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Principal Architect",
            "company_name": "Apple",
            "job_description": "Lead architecture for next-generation platform services.",
            "status": "saved",
        },
        headers=user_a_headers,
    )
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    # User A analyzes the job
    ana_res = await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=user_a_headers)
    assert ana_res.status_code == 200

    # User B attempts to access User A's job target -> 404
    b_get_res = await async_client.get(f"/api/v1/jobs/{job_id}", headers=user_b_headers)
    assert b_get_res.status_code == 404

    # User B attempts to access User A's job analysis -> 404
    b_ana_res = await async_client.get(f"/api/v1/jobs/{job_id}/analysis", headers=user_b_headers)
    assert b_ana_res.status_code == 404

    # User B attempts to trigger analysis on User A's job -> 404
    b_post_ana_res = await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=user_b_headers)
    assert b_post_ana_res.status_code == 404

    # User B attempts to list CV versions for User A's job -> empty or 404
    b_ver_res = await async_client.get(f"/api/v1/jobs/{job_id}/versions", headers=user_b_headers)
    assert b_ver_res.status_code == 200
    assert b_ver_res.json()["total"] == 0
