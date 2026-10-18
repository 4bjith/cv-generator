"""
Phase 8 — End-to-End Integration and Production-Readiness Test Suite.

Validates the complete 10-step user journey, multi-tenant isolation,
snapshot immutability, template switching, export pipelines, and live Gemini integration.
"""

import os
import uuid
import pytest
from httpx import AsyncClient

from app.core.config import get_settings
from app.ai.factory import clear_ai_provider_cache, get_ai_provider
from app.ai.gemini_provider import GeminiProvider
from app.schemas.tailoring import StructuredTailoringOutput
from app.schemas.cover_letter import StructuredCoverLetterOutput
from app.core.exceptions import InternalServerError


@pytest.fixture(autouse=True)
def reset_provider():
    clear_ai_provider_cache()
    yield
    clear_ai_provider_cache()


@pytest.mark.asyncio
async def test_complete_user_journey_end_to_end(async_client: AsyncClient):
    """
    Executes the complete 10-step applicant workflow end-to-end:
    1. Authentication & user isolation setup
    2. Master candidate profile & evidence management
    3. Job target creation & requirements analysis
    4. Clarification questions, answers & promotion
    5. Evidence-grounded AI CV tailoring
    6. Independent CV snapshot editing & immutability verification
    7. All six CV template configurations & presentation settings
    8. ATS compatibility & explainable keyword scoring
    9. Cover letter generation, editing, saving & regeneration
    10. Multipage PDF and DOCX binary exports
    """
    settings = get_settings()

    # =========================================================================
    # Step 1: Authentication & Registration (User A)
    # =========================================================================
    user_a_email = f"candidate.e2e.{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": user_a_email,
            "password": "SecurePassword123!",
            "full_name": "Jane Alexander",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    token_a = reg_resp.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify session profile (/auth/me)
    me_resp = await async_client.get("/api/v1/auth/me", headers=headers_a)
    assert me_resp.status_code == 200
    user_a_id = me_resp.json()["id"]

    # =========================================================================
    # Step 2: Master Candidate Profile & Evidence Management
    # =========================================================================
    profile_payload = {
        "first_name": "Jane",
        "last_name": "Alexander",
        "preferred_name": "Jane",
        "professional_headline": "Staff Distributed Systems Engineer",
        "email": user_a_email,
        "phone": "+1-555-019-2834",
        "city": "Seattle",
        "state": "WA",
        "country": "United States",
        "primary_title": "Staff Software Engineer",
        "secondary_titles": ["Distributed Systems Architect", "Cloud Infrastructure Lead"],
        "career_level": "staff",
        "industry": "Cloud Computing",
        "years_of_experience": 9.5,
        "specializations": ["High-Throughput Streaming", "Raft Consensus", "Kubernetes Operators"],
        "base_summary": "Staff engineer with 9+ years architecting fault-tolerant distributed platforms and telemetry backends.",
    }
    prof_resp = await async_client.post("/api/v1/profile", headers=headers_a, json=profile_payload)
    assert prof_resp.status_code == 201

    # Add work experience
    exp_resp = await async_client.post(
        "/api/v1/profile/experience",
        headers=headers_a,
        json={
            "company": "Hyperscale Cloud Corp",
            "position": "Senior Distributed Systems Engineer",
            "employment_type": "full_time",
            "location": "Seattle, WA",
            "start_date": "2021-03",
            "is_current": True,
            "description": "Led core storage engine team building multi-region consensus layer.",
            "responsibilities": ["Architected Paxos consensus cluster handling 2M IOPS", "Mentored 6 engineers"],
            "achievements": ["Reduced p99 replication latency by 42% through batch pipelining"],
            "technologies": ["Go", "Rust", "Raft", "gRPC", "Kubernetes", "Prometheus"],
            "metrics": [
                {"value": 2000000, "unit": "IOPS", "description": "Paxos cluster throughput"},
                {"value": 42, "unit": "%", "description": "p99 latency reduction"},
            ],
            "provenance": "user_provided",
        },
    )
    assert exp_resp.status_code == 201, exp_resp.text
    exp_id = exp_resp.json()["id"]

    # Add skill with relational linkage
    skill_resp = await async_client.post(
        "/api/v1/profile/skills",
        headers=headers_a,
        json={
            "name": "Distributed Consensus",
            "category": "backend",
            "proficiency": "expert",
            "years_of_experience": 6.0,
            "experience_ids": [exp_id],
            "provenance": "user_provided",
        },
    )
    assert skill_resp.status_code == 201, skill_resp.text
    skill_id = skill_resp.json()["id"]

    # Add verified evidence item
    ev_resp = await async_client.post(
        "/api/v1/profile/evidence",
        headers=headers_a,
        json={
            "title": "High-Throughput Paxos Benchmark Report",
            "source": "Production Benchmark System",
            "source_type": "metric_report",
            "description": "Production benchmark logs demonstrating 42% latency reduction and zero data loss over 72h chaos drill.",
            "verification_status": "verified",
            "associated_entities": [
                {"entity_type": "experience", "entity_id": exp_id}
            ],
        },
    )
    assert ev_resp.status_code == 201, ev_resp.text
    ev_id = ev_resp.json()["id"]

    # Profile strength check
    qs_resp = await async_client.get("/api/v1/profile/strength", headers=headers_a)
    assert qs_resp.status_code == 200
    assert qs_resp.json()["completion_percentage"] > 0

    # =========================================================================
    # Step 3: Job Target Creation & Requirement Analysis
    # =========================================================================
    job_resp = await async_client.post(
        "/api/v1/jobs",
        headers=headers_a,
        json={
            "title": "Lead Distributed Systems Architect",
            "company_name": "Nexus Infrastructure Inc",
            "location": "Remote / Seattle",
            "employment_type": "full_time",
            "job_description": """
            Nexus Infrastructure is seeking a Lead Distributed Systems Architect.
            Requirements:
            - 8+ years experience designing high-throughput distributed systems in Go or Rust.
            - Deep mastery of Raft or Paxos consensus protocols, replication, and fault tolerance.
            - Proven record reducing p99 tail latency on high-volume production microservices.
            - Expertise with Kubernetes orchestration, Prometheus observability, and chaos engineering.
            Preferred:
            - Experience leading cross-functional storage architecture initiatives.
            """,
            "status": "saved",
        },
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # Run requirement analysis
    analysis_resp = await async_client.post(f"/api/v1/jobs/{job_id}/analyze", headers=headers_a)
    assert analysis_resp.status_code == 200, analysis_resp.text
    analysis_data = analysis_resp.json()
    assert "analysis" in analysis_data or "requirements" in analysis_data or "job_id" in analysis_data

    # =========================================================================
    # Step 4: Clarification Questions, Answering & Promotion
    # =========================================================================
    clarif_resp = await async_client.get(f"/api/v1/jobs/{job_id}/clarifications", headers=headers_a)
    assert clarif_resp.status_code == 200
    clarif_session = clarif_resp.json()
    questions = clarif_session.get("questions", [])
    assert len(questions) > 0

    target_q = questions[0]
    q_id = target_q["id"]

    # Submit answer
    answer_resp = await async_client.post(
        f"/api/v1/jobs/{job_id}/clarifications/{q_id}/answer",
        headers=headers_a,
        json={"answer": "Directly led architecture for multi-region Raft cluster spanning 3 AWS zones with 99.999% uptime."},
    )
    assert answer_resp.status_code == 200

    # Promote answer into candidate profile knowledge base
    promote_resp = await async_client.post(
        f"/api/v1/jobs/{job_id}/clarifications/{q_id}/promote",
        headers=headers_a,
        json={"category": "experience"},
    )
    assert promote_resp.status_code == 200

    # =========================================================================
    # Step 5: Evidence-Grounded AI CV Tailoring
    # =========================================================================
    tailor_resp = await async_client.post(
        f"/api/v1/jobs/{job_id}/tailor-cv",
        headers=headers_a,
        json={
            "tone": "impact_driven",
            "focus_areas": ["Distributed Consensus", "Go", "Raft"],
        },
    )
    assert tailor_resp.status_code == 201, tailor_resp.text
    tailored_data = tailor_resp.json()
    cv_version_id = tailored_data["cv_version_id"]

    # =========================================================================
    # Step 6: Independent CV Snapshot Editing & Immutability Verification
    # =========================================================================
    version_resp = await async_client.get(f"/api/v1/cv/versions/{cv_version_id}", headers=headers_a)
    assert version_resp.status_code == 200
    v_data = version_resp.json()
    snapshot = v_data["content_snapshot"]

    # Update summary strictly on the snapshot
    updated_snapshot = dict(snapshot)
    updated_snapshot["basics"] = dict(updated_snapshot["basics"])
    updated_snapshot["basics"]["summary"] = "Custom tailored executive summary for Nexus Infrastructure."

    patch_resp = await async_client.patch(
        f"/api/v1/cv/versions/{cv_version_id}",
        headers=headers_a,
        json={
            "name": "Nexus Lead Architect — Final Review",
            "content_snapshot": updated_snapshot,
            "status": "ready",
        },
    )
    assert patch_resp.status_code == 200

    # Verify master profile was NOT mutated by the snapshot edit
    master_prof_check = await async_client.get("/api/v1/profile", headers=headers_a)
    assert master_prof_check.status_code == 200
    assert master_prof_check.json()["base_summary"] == profile_payload["base_summary"]
    assert master_prof_check.json()["base_summary"] != "Custom tailored executive summary for Nexus Infrastructure."

    # =========================================================================
    # Step 7: Six CV Templates & Presentation Settings
    # =========================================================================
    templates = [
        "modern-professional",
        "classic-executive",
        "ats-minimal",
        "technical-developer",
        "contemporary-two-column",
        "academic-research",
    ]
    for tmpl in templates:
        tmpl_update = await async_client.patch(
            f"/api/v1/cv/versions/{cv_version_id}",
            headers=headers_a,
            json={
                "content_snapshot": {
                    **updated_snapshot,
                    "presentation": {
                        "template": tmpl,
                        "page_size": "a4",
                        "spacing": "normal",
                        "color_scheme": "blue",
                        "typography": "sans",
                    },
                }
            },
        )
        assert tmpl_update.status_code == 200
        assert tmpl_update.json()["content_snapshot"]["presentation"]["template"] == tmpl

    # Export clean standard JSON Resume (without extensions)
    json_resume_resp = await async_client.get(
        f"/api/v1/cv/versions/{cv_version_id}/json-resume?apply_visibility=true",
        headers=headers_a,
    )
    assert json_resume_resp.status_code == 200
    jr = json_resume_resp.json()
    assert "basics" in jr
    assert jr["basics"]["name"] == "Jane Alexander"

    # =========================================================================
    # Step 8: ATS Compatibility & Explainable Keyword Scoring
    # =========================================================================
    ats_resp = await async_client.post(
        "/api/v1/ats/analyze",
        headers=headers_a,
        json={"cv_version_id": cv_version_id, "job_id": job_id},
    )
    assert ats_resp.status_code == 200
    ats_data = ats_resp.json()
    assert "overall_score" in ats_data
    assert "components" in ats_data
    assert 0 <= ats_data["overall_score"] <= 100

    # Apply grounded keyword suggestions into an independent new CV version snapshot
    grounded_sugs = [s for s in ats_data.get("suggestions", []) if s.get("is_grounded_in_profile")]
    if grounded_sugs:
        first_sug = grounded_sugs[0]
        apply_resp = await async_client.post(
            "/api/v1/ats/apply-suggestions",
            headers=headers_a,
            json={
                "cv_version_id": cv_version_id,
                "job_id": job_id,
                "new_version_name": "Nexus Architect ATS Optimized",
                "accepted_suggestion_ids": [first_sug["id"]],
            },
        )
        assert apply_resp.status_code == 201, apply_resp.text
        assert apply_resp.json()["new_version_id"] != cv_version_id
    else:
        # Verify that attempting to apply an ungrounded keyword triggers zero-hallucination validation
        ungrounded = [s for s in ats_data.get("suggestions", []) if not s.get("is_grounded_in_profile")]
        if ungrounded:
            bad_sug = ungrounded[0]
            unverified_apply = await async_client.post(
                "/api/v1/ats/apply-suggestions",
                headers=headers_a,
                json={
                    "cv_version_id": cv_version_id,
                    "job_id": job_id,
                    "new_version_name": "Nexus Unverified Reject",
                    "accepted_suggestion_ids": [bad_sug["id"]],
                },
            )
            assert unverified_apply.status_code == 422

    # =========================================================================
    # Step 9: Cover Letter Generation, Editing, Saving & Regeneration
    # =========================================================================
    cl_gen_resp = await async_client.post(
        "/api/v1/cover-letters/generate",
        headers=headers_a,
        json={
            "job_id": job_id,
            "cv_version_id": cv_version_id,
            "name": "Cover Letter — Nexus Infrastructure",
            "tone": "professional",
            "length_option": "standard",
            "additional_instructions": "Highlight Raft consensus engineering and chaos drill achievements.",
        },
    )
    assert cl_gen_resp.status_code == 201, cl_gen_resp.text
    letter_data = cl_gen_resp.json()
    letter_id = letter_data["id"]
    assert len(letter_data["body_paragraphs"]) > 0

    # Update cover letter
    cl_update_resp = await async_client.put(
        f"/api/v1/cover-letters/{letter_id}",
        headers=headers_a,
        json={
            "recipient_name": "Hiring Committee",
            "recipient_company": "Nexus Infrastructure",
            "salutation": "Dear Hiring Committee,",
            "opening": "I am thrilled to apply for the Lead Distributed Systems Architect role at Nexus Infrastructure.",
            "body_paragraphs": [
                "With 9+ years architecting fault-tolerant distributed platforms, I specialize in high-throughput streaming and Raft consensus.",
                "In my previous role, I reduced p99 replication latency by 42% through batch pipelining across 2M IOPS clusters.",
            ],
            "sign_off": "Sincerely,\nJane Alexander",
            "status": "ready",
        },
    )
    assert cl_update_resp.status_code == 200, cl_update_resp.text
    assert cl_update_resp.json()["status"] == "ready"

    # Regenerate with new version preservation
    cl_regen_resp = await async_client.post(
        f"/api/v1/cover-letters/{letter_id}/regenerate",
        headers=headers_a,
        json={
            "tone": "concise",
            "length_option": "short",
            "preserve_as_new_version": True,
            "new_name": "Nexus Infrastructure — Concise Version",
            "additional_instructions": "Sharpen focus on consensus resilience.",
        },
    )
    assert cl_regen_resp.status_code == 200, cl_regen_resp.text
    regen_data = cl_regen_resp.json()
    assert regen_data["id"] != letter_id
    assert regen_data["name"] == "Nexus Infrastructure — Concise Version"

    # Duplicate cover letter
    cl_dup_resp = await async_client.post(
        f"/api/v1/cover-letters/{letter_id}/duplicate",
        headers=headers_a,
    )
    assert cl_dup_resp.status_code == 201, cl_dup_resp.text
    assert cl_dup_resp.json()["id"] != letter_id

    # =========================================================================
    # Step 10: Multipage PDF and DOCX Exports
    # =========================================================================
    # CV PDF Export
    cv_pdf = await async_client.get(
        f"/api/v1/cv/versions/{cv_version_id}/export/pdf?template=modern-professional&page_size=a4",
        headers=headers_a,
    )
    assert cv_pdf.status_code == 200
    assert cv_pdf.headers["content-type"] == "application/pdf"
    assert cv_pdf.content.startswith(b"%PDF")

    # CV DOCX Export
    cv_docx = await async_client.get(
        f"/api/v1/cv/versions/{cv_version_id}/export/docx?template=classic-executive",
        headers=headers_a,
    )
    assert cv_docx.status_code == 200
    assert "openxmlformats" in cv_docx.headers["content-type"]
    assert cv_docx.content.startswith(b"PK")  # ZIP signature for docx

    # Cover Letter PDF Export
    cl_pdf = await async_client.get(
        f"/api/v1/cover-letters/{letter_id}/export/pdf",
        headers=headers_a,
    )
    assert cl_pdf.status_code == 200
    assert cl_pdf.content.startswith(b"%PDF")

    # Cover Letter DOCX Export
    cl_docx = await async_client.get(
        f"/api/v1/cover-letters/{letter_id}/export/docx",
        headers=headers_a,
    )
    assert cl_docx.status_code == 200
    assert cl_docx.content.startswith(b"PK")

    # =========================================================================
    # Step 11: Multi-Tenant User Isolation Audit
    # =========================================================================
    user_b_email = f"unauthorized.e2e.{uuid.uuid4().hex[:8]}@example.com"
    reg_b = await async_client.post(
        "/api/v1/auth/register",
        json={"email": user_b_email, "password": "Password456!", "full_name": "Bob Intruder"},
    )
    assert reg_b.status_code == 201
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    # User B cannot access User A's job target
    b_job_get = await async_client.get(f"/api/v1/jobs/{job_id}", headers=headers_b)
    assert b_job_get.status_code in (403, 404)

    # User B cannot update or delete User A's job target
    b_job_del = await async_client.delete(f"/api/v1/jobs/{job_id}", headers=headers_b)
    assert b_job_del.status_code in (403, 404)

    # User B cannot access User A's CV version
    b_cv_get = await async_client.get(f"/api/v1/cv/versions/{cv_version_id}", headers=headers_b)
    assert b_cv_get.status_code in (403, 404)

    # User B cannot export User A's CV version
    b_cv_exp = await async_client.get(f"/api/v1/cv/versions/{cv_version_id}/export/pdf", headers=headers_b)
    assert b_cv_exp.status_code in (403, 404)

    # User B cannot access or export User A's cover letter
    b_cl_get = await async_client.get(f"/api/v1/cover-letters/{letter_id}", headers=headers_b)
    assert b_cl_get.status_code in (403, 404)

    b_cl_exp = await async_client.get(f"/api/v1/cover-letters/{letter_id}/export/pdf", headers=headers_b)
    assert b_cl_exp.status_code in (403, 404)


@pytest.mark.asyncio
async def test_live_gemini_integration_end_to_end():
    """
    Validates actual live Google Gemini provider integration when GEMINI_API_KEY is configured.
    Tests generation, structured output with dereferencing, and embeddings over real Google APIs.
    Gracefully skips if GEMINI_API_KEY is not provisioned.
    """
    settings = get_settings()
    api_key = settings.gemini_api_key
    if not api_key or not api_key.strip():
        pytest.skip("GEMINI_API_KEY is not provisioned in backend/.env or environment. Skipping live Gemini test.")

    model_name = settings.gemini_model or "gemini-flash-latest"
    embedding_model = settings.gemini_embedding_model or "gemini-embedding-001"

    provider = GeminiProvider(
        api_key=api_key,
        model_name=model_name,
        embedding_model=embedding_model,
        timeout=45.0,
        max_retries=3,
    )

    try:
        # 1. Live text generation
        text_result = await provider.generate_text(
            prompt="Respond strictly with the single word: INTEGRATION_VERIFIED",
            max_tokens=300,
        )
        assert "INTEGRATION_VERIFIED" in text_result.strip()

        # 2. Live structured output with complex nested schema & $defs dereferencing
        structured_result = await provider.generate_structured(
            prompt="Generate a professional 2-paragraph cover letter for a Senior Site Reliability Engineer at CloudCorp.",
            schema=StructuredCoverLetterOutput,
        )
        assert isinstance(structured_result, StructuredCoverLetterOutput)
        assert len(structured_result.opening) > 10
        assert len(structured_result.body_paragraphs) >= 1

        # 3. Live vector embeddings
        embeddings = await provider.compute_embeddings([
            "Distributed consensus Raft protocol implementation in Go",
            "Kubernetes container orchestration and service mesh telemetry",
        ])
        assert len(embeddings) == 2
        assert len(embeddings[0]) > 0
        assert isinstance(embeddings[0][0], float)
    except InternalServerError as exc:
        if "rate limit" in str(exc).lower() or "quota" in str(exc).lower() or "resource_exhausted" in str(exc).lower():
            pytest.skip(f"External Google Gemini API quota currently exhausted on configured developer key: {exc}")
        raise
