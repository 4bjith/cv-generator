import uuid
import pytest
from httpx import AsyncClient

from app.models.autonomous_agent import JobSearchProfile
from app.repositories.postgres.autonomous_agent_repository import AutonomousAgentRepository
from app.services.discovery.evaluation_service import JobEvaluationService
from app.services.discovery.models import RawDiscoveredJob
from app.services.outreach.recruiter_service import RecruiterOutreachService


@pytest.mark.asyncio
async def test_job_search_profile_personal_defaults(async_client: AsyncClient):
    """Verifies that Abhijith AT's personal job search configuration is initialized with accurate defaults."""
    email = f"abhijith.{uuid.uuid4().hex[:6]}@example.com"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": "Abhijith AT"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch initial profile
    resp = await async_client.get("/api/v1/agent/profile", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "MERN Stack Developer" in data["target_roles"]
    assert "React Developer" in data["target_roles"]
    assert "JavaScript" in data["primary_skills"]
    assert "React" in data["primary_skills"]
    assert "Node.js" in data["primary_skills"]
    assert "Kannur" in data["target_locations"]
    assert "Kochi" in data["target_locations"]
    assert "Bangalore" in data["target_locations"]
    assert "Karnataka" in data["target_locations"]
    assert "Hyderabad" in data["target_locations"]
    assert "Telangana" in data["target_locations"]
    assert "Chennai" in data["target_locations"]
    assert "Tamil Nadu" in data["target_locations"]
    assert data["fresher_mode"] is True
    assert data["is_remote_prioritized"] is True
    assert data["auto_submit_enabled"] is False  # Safe supervised mode by default
    assert data["emergency_stopped"] is False

    # Update preferences
    update_resp = await async_client.put(
        "/api/v1/agent/profile",
        headers=headers,
        json={"daily_application_cap": 15, "auto_submit_enabled": True},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["daily_application_cap"] == 15
    assert update_resp.json()["auto_submit_enabled"] is True


@pytest.mark.asyncio
async def test_emergency_stop_and_resume(async_client: AsyncClient):
    """Verifies that the emergency stop switch instantly halts automated external execution."""
    email = f"agent.stop.{uuid.uuid4().hex[:6]}@example.com"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": "Candidate Test"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Emergency stop
    stop_resp = await async_client.post("/api/v1/agent/emergency-stop", headers=headers)
    assert stop_resp.status_code == 200
    assert stop_resp.json()["emergency_stopped"] is True
    assert stop_resp.json()["is_active"] is False

    # Attempting to run while stopped must fail
    run_resp = await async_client.post("/api/v1/agent/run-now", headers=headers)
    assert run_resp.status_code == 400
    assert "EMERGENCY STOPPED" in run_resp.json()["error"]["message"]

    # Resume agent
    resume_resp = await async_client.post("/api/v1/agent/resume", headers=headers)
    assert resume_resp.status_code == 200
    assert resume_resp.json()["emergency_stopped"] is False
    assert resume_resp.json()["is_active"] is True


def test_job_evaluation_fresher_friendly_and_rejection_rules():
    """Verifies that the evaluation service properly scores fresher MERN roles and rejects over-seniority/incompatible roles."""
    search_profile = JobSearchProfile(
        target_roles=["MERN Stack Developer", "React Developer", "Junior Software Engineer"],
        primary_skills=["JavaScript", "React", "Node.js", "Express.js", "MongoDB", "Git"],
        target_locations=["Remote", "Kannur", "Kochi", "Kerala"],
        is_remote_prioritized=True,
        fresher_mode=True,
    )

    # 1. High match fresher role
    fresher_job = RawDiscoveredJob(
        source_platform="greenhouse",
        external_id="gh_101",
        title="Junior MERN Stack Developer",
        company_name="TechCorp",
        location="Remote India",
        is_remote=True,
        employment_type="full_time",
        source_url="https://example.com/job/101",
        apply_url="https://example.com/job/101/apply",
        raw_description="Looking for Junior MERN Stack developer with knowledge of React, Node.js, Express, MongoDB and Git. Freshers with strong GitHub projects welcome.",
        extracted_skills=["React", "Node.Js", "Express.Js", "Mongodb", "Git"],
    )
    score, eligibility, reason = JobEvaluationService.evaluate_job(fresher_job, search_profile)
    assert score >= 80.0
    assert eligibility == "eligible"
    assert "Role match" in reason
    assert "Fresher fit" in reason

    # 2. Over-senior role rejected
    staff_job = RawDiscoveredJob(
        source_platform="lever",
        external_id="lev_202",
        title="Staff Principal Architect — Distributed Cloud",
        company_name="Enterprise Inc",
        location="Remote",
        is_remote=True,
        employment_type="full_time",
        source_url="https://example.com/job/202",
        apply_url="https://example.com/job/202/apply",
        raw_description="Requires 15+ years architecting enterprise distributed backends.",
    )
    score_staff, elig_staff, reason_staff = JobEvaluationService.evaluate_job(staff_job, search_profile)
    assert score_staff < 40.0
    assert elig_staff == "ineligible"
    assert "exceeds early-career target scope" in reason_staff

    # 3. Location mismatch rejected
    onsite_unapproved = RawDiscoveredJob(
        source_platform="portal",
        external_id="ext_303",
        title="Junior Web Developer",
        company_name="Local Firm",
        location="Onsite only - Sydney, Australia",
        is_remote=False,
        employment_type="full_time",
        source_url="https://example.com/job/303",
        apply_url="https://example.com/job/303/apply",
        raw_description="Must be located in Sydney and work from office.",
    )
    score_loc, elig_loc, reason_loc = JobEvaluationService.evaluate_job(onsite_unapproved, search_profile)
    assert elig_loc == "ineligible"
    assert "outside target regions" in reason_loc

    # 4. Onsite South India (Bangalore / Karnataka) accepted
    search_profile_south = JobSearchProfile(
        target_roles=["MERN Stack Developer", "React Developer"],
        primary_skills=["JavaScript", "React", "Node.js", "Express.js", "MongoDB", "Git"],
        target_locations=[
            "Remote",
            "India",
            "Bangalore",
            "Bengaluru",
            "Karnataka",
            "Hyderabad",
            "Telangana",
            "Chennai",
            "Coimbatore",
            "Tamil Nadu",
            "Kochi",
            "Kerala",
        ],
        is_remote_prioritized=True,
        fresher_mode=True,
    )
    bengaluru_job = RawDiscoveredJob(
        source_platform="portal",
        external_id="beng_404",
        title="Junior React Developer",
        company_name="Bangalore Tech Hub",
        location="Bengaluru, Karnataka",
        is_remote=False,
        employment_type="full_time",
        source_url="https://example.com/job/404",
        apply_url="https://example.com/job/404/apply",
        raw_description="Looking for an entry-level React developer in Bangalore.",
        extracted_skills=["React", "Javascript", "Html", "Css"],
    )
    score_beng, elig_beng, reason_beng = JobEvaluationService.evaluate_job(bengaluru_job, search_profile_south)
    assert score_beng >= 70.0
    assert elig_beng == "eligible"
    assert "Role match" in reason_beng


@pytest.mark.asyncio
async def test_qa_memory_bank_operations(async_client: AsyncClient):
    """Verifies that the QA Memory Bank properly stores, matches, and retrieves verified application answers."""
    email = f"qa.test.{uuid.uuid4().hex[:6]}@example.com"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": "QA Candidate"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch auto-seeded QA items
    qa_list_resp = await async_client.get("/api/v1/agent/qa-bank", headers=headers)
    assert qa_list_resp.status_code == 200
    items = qa_list_resp.json()
    assert len(items) >= 5

    # Check work authorization and notice period presence
    patterns = [i["question_pattern"] for i in items]
    assert any("authorized to work" in p for p in patterns)
    assert any("notice period" in p for p in patterns)

    # Add custom QA item
    new_qa = await async_client.post(
        "/api/v1/agent/qa-bank",
        headers=headers,
        json={
            "category": "custom",
            "question_pattern": "preferred code editor",
            "answer_value": "Visual Studio Code with vim keybindings",
            "is_confirmed": True,
            "user_notes": "Favorite development environment",
        },
    )
    assert new_qa.status_code == 201
    created_id = new_qa.json()["id"]

    # Delete custom QA item
    del_resp = await async_client.delete(f"/api/v1/agent/qa-bank/{created_id}", headers=headers)
    assert del_resp.status_code == 204


def test_recruiter_outreach_constraints():
    """Verifies that recruiter outreach generation adheres to character limits and evidence grounding."""
    service = RecruiterOutreachService(repo=None)  # type: ignore

    note = service.generate_linkedin_connection_note(
        candidate_name="Abhijith AT",
        recruiter_name="Sarah Jenkins",
        role_title="React Developer",
        company_name="Razorpay",
        highlight_skill_or_project="React and Node.js solutions",
    )
    # Strict LinkedIn character constraint
    assert len(note) <= 300
    assert "Sarah" in note
    assert "React Developer" in note
    assert "Razorpay" in note

    email = service.generate_recruiter_email(
        candidate_name="Abhijith AT",
        recruiter_name="Hiring Team",
        role_title="MERN Stack Developer",
        company_name="Postman",
    )
    assert len(email.split()) < 150  # Executive concise email
    assert "https://4bjith.github.io/Portfolio-Website/" in email
    assert "https://github.com/4bjith/" in email


@pytest.mark.asyncio
async def test_full_agent_cycle_and_daily_report_generation(async_client: AsyncClient):
    """Verifies that an on-demand agent run discovers jobs, tailors applications, and produces a daily briefing."""
    email = f"agent.e2e.{uuid.uuid4().hex[:6]}@example.com"
    reg = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "SecurePassword123!", "full_name": "Abhijith AT"},
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Run agent full cycle on-demand (limit to 2 applications)
    run_resp = await async_client.post("/api/v1/agent/run-now?max_applications=2", headers=headers)
    assert run_resp.status_code == 200, run_resp.text
    result = run_resp.json()
    assert result["status"] == "completed"
    assert result["jobs_found"] >= 3
    assert result["applications_prepared"] >= 1 or result["applications_submitted"] >= 1
    assert result["report"] is not None
    assert "Daily Career Agent Report" in result["report"]["summary_markdown"]

    # Verify latest report API
    report_resp = await async_client.get("/api/v1/agent/reports/latest", headers=headers)
    assert report_resp.status_code == 200
    assert report_resp.json() is not None
    assert report_resp.json()["jobs_discovered_count"] >= 3

    # Verify discovered jobs API
    jobs_resp = await async_client.get("/api/v1/agent/jobs", headers=headers)
    assert jobs_resp.status_code == 200
    assert len(jobs_resp.json()) >= 3

    # Verify applications tracking API
    apps_resp = await async_client.get("/api/v1/agent/applications", headers=headers)
    assert apps_resp.status_code == 200
    assert len(apps_resp.json()) >= 1
