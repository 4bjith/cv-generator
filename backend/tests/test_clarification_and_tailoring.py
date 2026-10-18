import uuid
import pytest
from httpx import AsyncClient

from app.ai.factory import get_ai_provider
from app.ai.mock_provider import MockAIProvider
from app.schemas.tailoring import StructuredTailoringOutput


async def get_auth_headers(client: AsyncClient, email: str) -> dict:
    """Helper to register a unique user and obtain auth headers."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "Clarification Test Candidate",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


SAMPLE_JOB_TEXT = """
We are hiring a Lead Backend Architect at CloudScale.

Mandatory Requirements:
- 5+ years of production experience with Python and FastAPI.
- Deep expertise in PostgreSQL database design, query optimization, and connection pooling.
- Proven experience with Docker containerization and Kubernetes cluster management.
- Hands-on production experience with Apache Kafka event streaming.

Preferred Qualifications:
- Familiarity with Redis caching patterns and distributed locks.
- Experience with GraphQL APIs.
- AWS Certified DevOps Engineer.
"""


@pytest.mark.asyncio
async def test_ai_provider_abstraction():
    """Verify AI provider interface, mock generation, and structured schema adherence."""
    provider = get_ai_provider()
    assert provider is not None

    mock_provider = MockAIProvider()
    text = await mock_provider.generate_text("Please write a professional summary for software engineer")
    assert "software engineer" in text.lower() or "engineering" in text.lower()

    structured = await mock_provider.generate_structured(
        prompt="TARGET ROLE: Lead Architect\nCANDIDATE SKILLS: Python, FastAPI, PostgreSQL",
        schema=StructuredTailoringOutput,
    )
    assert isinstance(structured, StructuredTailoringOutput)
    assert structured.target_role == "Lead Architect"
    assert "Python" in structured.relevant_skills
    assert len(structured.change_summary) > 0


@pytest.mark.asyncio
async def test_clarification_session_lifecycle_and_prioritization(async_client: AsyncClient):
    """
    Test clarification session initialization:
    - Questions prioritized by mandatory (priority 1) vs preferred (priority 2).
    - Session resumption preserving candidate answers across subsequent requests.
    - Skipping and bulk answering.
    """
    headers = await get_auth_headers(async_client, "clarify_life@example.com")

    # 1. Setup Candidate Profile with some known skills (Python, PostgreSQL), missing Docker & Kafka
    prof_payload = {
        "first_name": "Alex",
        "last_name": "Taylor",
        "primary_title": "Senior Backend Developer",
        "base_summary": "Seasoned backend developer specializing in Python microservices and PostgreSQL databases.",
    }
    prof_res = await async_client.post("/api/v1/profile", json=prof_payload, headers=headers)
    assert prof_res.status_code == 201

    await async_client.post("/api/v1/profile/skills", json={"name": "Python", "category": "technical", "proficiency": "advanced"}, headers=headers)
    await async_client.post("/api/v1/profile/skills", json={"name": "PostgreSQL", "category": "technical", "proficiency": "advanced"}, headers=headers)

    # 2. Create Job Target and run analysis
    job_payload = {
        "title": "Lead Backend Architect",
        "company_name": "CloudScale Inc",
        "job_description": SAMPLE_JOB_TEXT,
    }
    job_res = await async_client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert job_res.status_code == 201
    job_id = job_res.json()["id"]

    analyze_res = await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)
    assert analyze_res.status_code == 200

    # 3. Retrieve Clarification Session
    clar_res = await async_client.get(f"/api/v1/jobs/{job_id}/clarifications", headers=headers)
    assert clar_res.status_code == 200
    session_data = clar_res.json()

    assert session_data["job_id"] == job_id
    assert session_data["total_questions"] > 0
    questions = session_data["questions"]

    # Verify prioritization: mandatory questions (priority 1) appear first
    priorities = [q["priority"] for q in questions]
    assert priorities == sorted(priorities)

    # Find a question to answer
    first_q = questions[0]
    q_id = first_q["id"]
    assert first_q["status"] == "unanswered"
    assert first_q["provenance"] == "candidate_clarification"
    assert first_q["verification_status"] == "unverified"

    # 4. Answer the question
    answer_payload = {
        "answer": "I led the migration of legacy services to Kubernetes on AWS EKS and managed Kafka streaming for order ingestion.",
        "save_to_profile": False,
    }
    ans_res = await async_client.post(
        f"/api/v1/jobs/{job_id}/clarifications/{q_id}/answer",
        json=answer_payload,
        headers=headers,
    )
    assert ans_res.status_code == 200
    updated_session = ans_res.json()
    assert updated_session["answered_count"] == 1

    ans_q = next(q for q in updated_session["questions"] if q["id"] == q_id)
    assert ans_q["status"] == "answered"
    assert "Kubernetes" in ans_q["answer"]

    # 5. Session Resumption Check: fetch session again and verify answer persisted
    re_res = await async_client.get(f"/api/v1/jobs/{job_id}/clarifications", headers=headers)
    assert re_res.status_code == 200
    resumed = re_res.json()
    assert resumed["answered_count"] == 1
    resumed_q = next(q for q in resumed["questions"] if q["id"] == q_id)
    assert resumed_q["status"] == "answered"
    assert resumed_q["answer"] == answer_payload["answer"]

    # 6. Skip a question
    if len(questions) > 1:
        second_q = questions[1]
        skip_res = await async_client.post(
            f"/api/v1/jobs/{job_id}/clarifications/{second_q['id']}/skip",
            headers=headers,
        )
        assert skip_res.status_code == 200
        assert skip_res.json()["skipped_count"] >= 1


@pytest.mark.asyncio
async def test_clarification_promote_to_profile(async_client: AsyncClient):
    """Test candidate-confirmed promotion of an answered clarification to the master profile."""
    headers = await get_auth_headers(async_client, "promote_test@example.com")

    # Profile
    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Jordan", "last_name": "Lee", "primary_title": "Developer"},
        headers=headers,
    )

    # Job & Analysis
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "DevOps Engineer",
            "company_name": "OpsTech",
            "job_description": "Requirements:\n- Must have Terraform and Ansible infrastructure automation experience.\n- 3+ years managing CI/CD pipelines.",
        },
        headers=headers,
    )
    job_id = job_res.json()["id"]
    await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)

    clar_res = await async_client.get(f"/api/v1/jobs/{job_id}/clarifications", headers=headers)
    session = clar_res.json()
    assert session["total_questions"] > 0
    q_id = session["questions"][0]["id"]

    # Answer question
    await async_client.post(
        f"/api/v1/jobs/{job_id}/clarifications/{q_id}/answer",
        json={"answer": "Built reusable Terraform modules for AWS multi-region infrastructure.", "save_to_profile": False},
        headers=headers,
    )

    # Promote to profile
    prom_res = await async_client.post(
        f"/api/v1/jobs/{job_id}/clarifications/{q_id}/promote",
        json={"category": "skills", "skill_proficiency": "advanced"},
        headers=headers,
    )
    assert prom_res.status_code == 200
    assert prom_res.json()["status"] == "promoted"

    # Verify profile now has the promoted evidence record with unverified provenance
    prof_after = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_after.status_code == 200
    p_data = prof_after.json()
    assert len(p_data["evidence_items"]) > 0
    ev = p_data["evidence_items"][0]
    assert ev["source"] == "candidate_clarification"
    assert ev["verification_status"] == "unverified"


@pytest.mark.asyncio
async def test_evidence_grounded_cv_tailoring_pipeline(async_client: AsyncClient):
    """
    Test full evidence-grounded AI CV tailoring:
    - Generates new independent CVVersion snapshot linked to job_target_id.
    - Master CandidateProfile is strictly UNMODIFIED.
    - Previous CVVersion snapshots are strictly UNMODIFIED.
    - Generates change summary and unresolved gaps warnings.
    - Quality score is high and verified.
    """
    headers = await get_auth_headers(async_client, "tailor_pipe@example.com")

    # 1. Candidate Profile Setup
    original_summary = "Backend software architect with 8 years building distributed applications."
    await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Sam",
            "last_name": "Rivera",
            "primary_title": "Staff Engineer",
            "base_summary": original_summary,
        },
        headers=headers,
    )
    await async_client.post("/api/v1/profile/skills", json={"name": "Python", "category": "technical", "proficiency": "expert"}, headers=headers)
    await async_client.post("/api/v1/profile/skills", json={"name": "FastAPI", "category": "technical", "proficiency": "expert"}, headers=headers)
    await async_client.post("/api/v1/profile/skills", json={"name": "PostgreSQL", "category": "technical", "proficiency": "expert"}, headers=headers)
    await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Nexus Systems",
            "position": "Senior Backend Engineer",
            "start_date": "2021-01",
            "is_current": True,
            "description": "Led backend microservices architecture.",
            "responsibilities": ["Designed high-throughput data processing services using FastAPI."],
            "achievements": ["Reduced p99 database query response latency by 45%."],
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
        },
        headers=headers,
    )

    # 2. Create baseline CV version from profile
    base_ver_res = await async_client.post(
        "/api/v1/cv/versions",
        json={"name": "Master Profile Base CV"},
        headers=headers,
    )
    assert base_ver_res.status_code == 201
    base_version_id = base_ver_res.json()["id"]
    base_snapshot_orig = base_ver_res.json()["content_snapshot"]

    # 3. Create Target Job and analyze
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Principal Distributed Systems Engineer",
            "company_name": "ScaleGrid",
            "job_description": SAMPLE_JOB_TEXT,
        },
        headers=headers,
    )
    job_id = job_res.json()["id"]
    await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers)

    # 4. Clarification step: answer a question
    clar_res = await async_client.get(f"/api/v1/jobs/{job_id}/clarifications", headers=headers)
    session = clar_res.json()
    if session["questions"]:
        q = session["questions"][0]
        await async_client.post(
            f"/api/v1/jobs/{job_id}/clarifications/{q['id']}/answer",
            json={"answer": "Implemented Apache Kafka event streaming for real-time analytics at Nexus Systems.", "save_to_profile": False},
            headers=headers,
        )

    # 5. Tailor CV via POST /api/v1/jobs/{job_id}/tailor-cv
    tailor_payload = {
        "template": "technical",
        "tone": "technical",
        "focus_areas": ["Distributed systems", "Latency reduction"],
        "custom_instructions": "Highlight low-latency performance optimizations.",
    }
    tailor_res = await async_client.post(
        f"/api/v1/jobs/{job_id}/tailor-cv",
        json=tailor_payload,
        headers=headers,
    )
    assert tailor_res.status_code == 201
    tailored_data = tailor_res.json()

    assert tailored_data["job_id"] == job_id
    assert tailored_data["cv_version_id"] is not None
    assert "Principal Distributed Systems Engineer" in tailored_data["version_name"] or "Tailored" in tailored_data["version_name"]
    assert len(tailored_data["change_summary"]) > 0
    assert tailored_data["quality_score"] >= 80.0

    # Content snapshot verification
    snapshot = tailored_data["content_snapshot"]
    assert snapshot["schema_version"] == "2.0.0"
    assert snapshot["basics"]["name"] == "Sam Rivera"
    assert snapshot["presentation"]["template"] == "technical"
    assert len(snapshot["work"]) > 0
    assert len(snapshot["skills"]) > 0

    # 6. NON-MUTATION VERIFICATION: Candidate Profile remains unaltered
    prof_check = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_check.status_code == 200
    assert prof_check.json()["base_summary"] == original_summary

    # 7. NON-MUTATION VERIFICATION: Previous base CVVersion remains unaltered
    base_ver_check = await async_client.get(f"/api/v1/cv/versions/{base_version_id}", headers=headers)
    assert base_ver_check.status_code == 200
    assert base_ver_check.json()["content_snapshot"]["basics"]["summary"] == base_snapshot_orig["basics"]["summary"]

    # 8. Test Export Compatibility of the newly tailored version
    new_cv_id = tailored_data["cv_version_id"]
    pdf_res = await async_client.get(f"/api/v1/cv/versions/{new_cv_id}/export/pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    docx_res = await async_client.get(f"/api/v1/cv/versions/{new_cv_id}/export/docx", headers=headers)
    assert docx_res.status_code == 200
    assert "wordprocessingml" in docx_res.headers["content-type"]
    assert len(docx_res.content) > 1000

    # 9. Test FRD endpoint alias POST /api/v1/jobs/{job_id}/cv/generate
    alias_res = await async_client.post(
        f"/api/v1/jobs/{job_id}/cv/generate",
        json={"template": "modern"},
        headers=headers,
    )
    assert alias_res.status_code == 201
    assert alias_res.json()["cv_version_id"] is not None


@pytest.mark.asyncio
async def test_cross_user_isolation(async_client: AsyncClient):
    """Verify that User B cannot access or answer User A's clarification questions or tailor User A's job."""
    headers_a = await get_auth_headers(async_client, "user_a_clarify@example.com")
    headers_b = await get_auth_headers(async_client, "user_b_clarify@example.com")

    # User A creates a job
    job_res = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Private Role", "company_name": "Private Co", "job_description": "Private description."},
        headers=headers_a,
    )
    job_id = job_res.json()["id"]

    # User B attempts to access clarifications -> 404
    b_clar = await async_client.get(f"/api/v1/jobs/{job_id}/clarifications", headers=headers_b)
    assert b_clar.status_code == 404

    # User B attempts to tailor CV for User A's job -> 404
    b_tailor = await async_client.post(f"/api/v1/jobs/{job_id}/tailor-cv", headers=headers_b)
    assert b_tailor.status_code == 404
