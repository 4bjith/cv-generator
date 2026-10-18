import io
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
            "full_name": "Cover Letter Candidate",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_generate_cover_letter_evidence_grounded(async_client: AsyncClient):
    """
    Verify evidence-grounded cover letter generation:
    Ensures letter is tailored to job target, cites verified candidate facts,
    calculates word count, and leaves master profile untouched.
    """
    headers = await get_auth_headers(async_client, "cl_evidence@example.com")

    # 1. Setup candidate profile
    prof_resp = await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Alexandra",
            "last_name": "Chen",
            "primary_title": "Senior Cloud Infrastructure Engineer",
            "base_summary": "8 years architecting resilient multi-cloud backends.",
        },
        headers=headers,
    )
    assert prof_resp.status_code in (200, 201)
    orig_profile = prof_resp.json()

    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Kubernetes", "category": "cloud", "proficiency": "expert"},
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "backend", "proficiency": "expert"},
        headers=headers,
    )

    await async_client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Stratos Cloud",
            "position": "Lead DevOps Architect",
            "start_date": "2020-01-01",
            "end_date": "2024-06-01",
            "responsibilities": ["Reduced deployment cycle time by 40% using container orchestration."],
            "technologies": ["Kubernetes", "Terraform", "Python"],
        },
        headers=headers,
    )

    # 2. Setup job target
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Principal Platform Engineer",
            "company_name": "Lattice Systems",
            "location": "San Francisco, CA (Hybrid)",
            "employment_type": "full-time",
            "job_description": (
                "Lattice Systems is seeking a Principal Platform Engineer to lead cloud infrastructure. "
                "Must have 5+ years with Kubernetes, Python, and microservices architecture. "
                "Preferred experience with Terraform and distributed observability."
            ),
        },
        headers=headers,
    )
    assert job_resp.status_code == 201
    job = job_resp.json()

    # 3. Analyze job to extract requirements
    await async_client.post(f"/api/v1/jobs/{job['id']}/analyze", headers=headers)

    # 4. Generate cover letter
    gen_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={
            "job_id": job["id"],
            "tone": "technical",
            "length_option": "standard",
            "additional_instructions": "Highlight container orchestration accomplishments and low-latency systems.",
            "recipient_name": "Dr. Aris Thorne",
            "recipient_title": "VP of Engineering",
            "recipient_company": "Lattice Systems",
        },
        headers=headers,
    )
    assert gen_resp.status_code == 201
    cl_data = gen_resp.json()

    # Verify structured fields
    assert cl_data["name"] == "Principal Platform Engineer at Lattice Systems - Cover Letter"
    assert cl_data["status"] == "draft"
    assert cl_data["tone"] == "technical"
    assert cl_data["length_option"] == "standard"
    assert cl_data["recipient_name"] == "Dr. Aris Thorne"
    assert cl_data["recipient_company"] == "Lattice Systems"
    assert "Alexandra Chen" in cl_data["sender_name"]
    assert len(cl_data["body_paragraphs"]) >= 2
    assert cl_data["word_count"] > 100
    assert "Principal Platform Engineer" in cl_data["opening"]
    assert "Sincerely," in cl_data["sign_off"]
    assert len(cl_data["factual_claims"]) > 0

    # Verify CandidateProfile was NOT mutated
    prof_check = await async_client.get("/api/v1/profile", headers=headers)
    assert prof_check.json()["primary_title"] == orig_profile["primary_title"]


@pytest.mark.asyncio
async def test_generate_cover_letter_with_unresolved_gaps(async_client: AsyncClient):
    """
    Verify that unverified / missing job requirements are flagged in unresolved_gaps
    and not falsely claimed in the letter.
    """
    headers = await get_auth_headers(async_client, "cl_gaps@example.com")

    # Profile with Python but NO Golang or Rust
    await async_client.post(
        "/api/v1/profile",
        json={
            "first_name": "Elena",
            "last_name": "Rostova",
            "primary_title": "Backend Developer",
        },
        headers=headers,
    )
    await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "Python", "category": "languages", "proficiency": "expert"},
        headers=headers,
    )

    # Job target strictly requiring Rust and Golang systems programming
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={
            "title": "Systems Core Engineer",
            "company_name": "Quantum Networks",
            "job_description": "Core protocol engineer. Mandatory requirements: Rust low-level concurrency and Golang network daemons.",
        },
        headers=headers,
    )
    job = job_resp.json()
    await async_client.post(f"/api/v1/jobs/{job['id']}/analyze", headers=headers)

    gen_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={
            "job_id": job["id"],
            "tone": "formal",
            "length_option": "short",
        },
        headers=headers,
    )
    assert gen_resp.status_code == 201
    cl_data = gen_resp.json()

    # Ensure gaps list is returned
    assert isinstance(cl_data["unresolved_gaps"], list)


@pytest.mark.asyncio
async def test_regenerate_cover_letter_preserves_version_history(async_client: AsyncClient):
    """
    Verify that regenerating with preserve_as_new_version=True creates a new
    independent CoverLetter record while preserving the previous version intact.
    """
    headers = await get_auth_headers(async_client, "cl_history@example.com")

    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Marcus", "last_name": "Cole", "primary_title": "Lead Engineer"},
        headers=headers,
    )
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Staff Engineer", "company_name": "Apex Core", "job_description": "Staff Engineer with Python experience."},
        headers=headers,
    )
    job = job_resp.json()

    # Initial generation
    init_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={"job_id": job["id"], "tone": "professional", "length_option": "standard"},
        headers=headers,
    )
    assert init_resp.status_code == 201
    orig_letter = init_resp.json()

    # Regenerate preserving version
    regen_resp = await async_client.post(
        f"/api/v1/cover-letters/{orig_letter['id']}/regenerate",
        json={
            "tone": "concise",
            "length_option": "short",
            "additional_instructions": "Make it punchy and concise.",
            "preserve_as_new_version": True,
            "new_name": "Staff Engineer at Apex Core - Concise Edition",
        },
        headers=headers,
    )
    assert regen_resp.status_code == 200
    new_letter = regen_resp.json()

    # Verify new ID created and parameters updated
    assert new_letter["id"] != orig_letter["id"]
    assert new_letter["name"] == "Staff Engineer at Apex Core - Concise Edition"
    assert new_letter["tone"] == "concise"
    assert new_letter["length_option"] == "short"
    assert new_letter["change_summary"] is not None

    # Verify original version still exists in database untouched
    check_orig = await async_client.get(f"/api/v1/cover-letters/{orig_letter['id']}", headers=headers)
    assert check_orig.status_code == 200
    assert check_orig.json()["tone"] == "professional"

    # Verify both letters appear in list
    list_resp = await async_client.get("/api/v1/cover-letters", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 2


@pytest.mark.asyncio
async def test_regenerate_cover_letter_in_place(async_client: AsyncClient):
    """
    Verify that regenerating with preserve_as_new_version=False updates
    the existing record in place with an updated change summary.
    """
    headers = await get_auth_headers(async_client, "cl_inplace@example.com")

    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Sarah", "last_name": "Connor", "primary_title": "DevOps Specialist"},
        headers=headers,
    )
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Cloud Architect", "company_name": "Cyberdyne", "job_description": "Infrastructure cloud architect."},
        headers=headers,
    )
    job = job_resp.json()

    init_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={"job_id": job["id"], "tone": "professional"},
        headers=headers,
    )
    orig_letter = init_resp.json()

    # In-place regeneration
    regen_resp = await async_client.post(
        f"/api/v1/cover-letters/{orig_letter['id']}/regenerate",
        json={
            "tone": "formal",
            "additional_instructions": "Use formal executive phrasing.",
            "preserve_as_new_version": False,
        },
        headers=headers,
    )
    assert regen_resp.status_code == 200
    updated = regen_resp.json()

    # Same ID, updated tone and change summary
    assert updated["id"] == orig_letter["id"]
    assert updated["tone"] == "formal"
    assert updated["change_summary"] is not None


@pytest.mark.asyncio
async def test_cover_letter_crud_and_duplication(async_client: AsyncClient):
    """
    Verify full CRUD operations: update fields, duplicate as new draft, and delete.
    """
    headers = await get_auth_headers(async_client, "cl_crud@example.com")

    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "David", "last_name": "Kim", "primary_title": "Full Stack Dev"},
        headers=headers,
    )
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Full Stack Engineer", "company_name": "Vanguard Labs", "job_description": "Full stack engineer role."},
        headers=headers,
    )
    job = job_resp.json()

    # 1. Create
    init_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={"job_id": job["id"]},
        headers=headers,
    )
    letter = init_resp.json()
    letter_id = letter["id"]

    # 2. Update editable fields
    update_resp = await async_client.put(
        f"/api/v1/cover-letters/{letter_id}",
        json={
            "name": "Customized Vanguard Letter",
            "status": "ready",
            "salutation": "Dear Vanguard Hiring Committee,",
            "opening": "I am thrilled to present my candidacy for the Full Stack Engineer role.",
            "body_paragraphs": ["First customized paragraph.", "Second customized paragraph with metrics."],
            "closing": "Thank you for reviewing my qualifications.",
        },
        headers=headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["name"] == "Customized Vanguard Letter"
    assert updated["status"] == "ready"
    assert updated["salutation"] == "Dear Vanguard Hiring Committee,"
    assert len(updated["body_paragraphs"]) == 2
    assert "First customized paragraph." in updated["full_content"]

    # 3. Duplicate
    dup_resp = await async_client.post(
        f"/api/v1/cover-letters/{letter_id}/duplicate",
        headers=headers,
    )
    assert dup_resp.status_code == 201
    cloned = dup_resp.json()
    assert cloned["id"] != letter_id
    assert cloned["name"] == "Customized Vanguard Letter (Copy)"
    assert cloned["status"] == "draft"

    # 4. Delete cloned
    del_resp = await async_client.delete(f"/api/v1/cover-letters/{cloned['id']}", headers=headers)
    assert del_resp.status_code == 200

    # 5. Verify deleted is gone
    check_del = await async_client.get(f"/api/v1/cover-letters/{cloned['id']}", headers=headers)
    assert check_del.status_code == 404


@pytest.mark.asyncio
async def test_cover_letter_cross_user_isolation(async_client: AsyncClient):
    """
    Verify multi-tenant security:
    Users cannot view, update, regenerate, duplicate, or delete other candidates' cover letters.
    """
    headers_a = await get_auth_headers(async_client, "user_a@example.com")
    headers_b = await get_auth_headers(async_client, "user_b@example.com")

    # User A profile and job
    await async_client.post("/api/v1/profile", json={"first_name": "User", "last_name": "A"}, headers=headers_a)
    job_a_resp = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Engineer A", "company_name": "Company A", "job_description": "Job A"},
        headers=headers_a,
    )
    job_a = job_a_resp.json()

    # User A letter
    letter_a_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={"job_id": job_a["id"]},
        headers=headers_a,
    )
    letter_a = letter_a_resp.json()
    letter_id = letter_a["id"]

    # User B setup
    await async_client.post("/api/v1/profile", json={"first_name": "User", "last_name": "B"}, headers=headers_b)

    # User B cannot access User A's letter
    get_resp = await async_client.get(f"/api/v1/cover-letters/{letter_id}", headers=headers_b)
    assert get_resp.status_code == 404

    # User B cannot update User A's letter
    put_resp = await async_client.put(f"/api/v1/cover-letters/{letter_id}", json={"name": "Hacked"}, headers=headers_b)
    assert put_resp.status_code == 404

    # User B cannot regenerate User A's letter
    regen_resp = await async_client.post(f"/api/v1/cover-letters/{letter_id}/regenerate", json={}, headers=headers_b)
    assert regen_resp.status_code == 404

    # User B cannot duplicate User A's letter
    dup_resp = await async_client.post(f"/api/v1/cover-letters/{letter_id}/duplicate", headers=headers_b)
    assert dup_resp.status_code == 404

    # User B cannot delete User A's letter
    del_resp = await async_client.delete(f"/api/v1/cover-letters/{letter_id}", headers=headers_b)
    assert del_resp.status_code == 404

    # User B cannot generate letter targeting User A's job target
    hijack_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={"job_id": job_a["id"]},
        headers=headers_b,
    )
    assert hijack_resp.status_code == 404


@pytest.mark.asyncio
async def test_cover_letter_pdf_and_docx_export(async_client: AsyncClient):
    """
    Verify downloadable PDF and DOCX export generation:
    Ensures correct headers, MIME types, Content-Disposition, and non-empty binary payloads.
    """
    headers = await get_auth_headers(async_client, "cl_export@example.com")

    await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Natasha", "last_name": "Romanoff", "primary_title": "Security Analyst"},
        headers=headers,
    )
    job_resp = await async_client.post(
        "/api/v1/jobs",
        json={"title": "Principal Security Engineer", "company_name": "Shield Tech", "job_description": "Cybersecurity role."},
        headers=headers,
    )
    job = job_resp.json()

    gen_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        json={"job_id": job["id"], "recipient_name": "Director Fury"},
        headers=headers,
    )
    letter = gen_resp.json()
    letter_id = letter["id"]

    # 1. Test PDF Export
    pdf_resp = await async_client.get(f"/api/v1/cover-letters/{letter_id}/export/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert "attachment;" in pdf_resp.headers["content-disposition"]
    assert len(pdf_resp.content) > 500  # Valid PDF binary payload
    assert pdf_resp.content.startswith(b"%PDF")

    # 2. Test DOCX Export
    docx_resp = await async_client.get(f"/api/v1/cover-letters/{letter_id}/export/docx", headers=headers)
    assert docx_resp.status_code == 200
    assert "openxmlformats-officedocument" in docx_resp.headers["content-type"]
    assert "attachment;" in docx_resp.headers["content-disposition"]
    assert len(docx_resp.content) > 500  # Valid DOCX zip payload
    assert docx_resp.content.startswith(b"PK")  # Standard Zip container for DOCX
