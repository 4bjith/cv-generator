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
            "full_name": "Alex Mercer",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_and_get_profile(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "create_get@example.com")

    # 1. Profile does not exist yet -> 404
    get_res = await async_client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 404

    # 2. Create profile
    payload = {
        "first_name": "Alex",
        "last_name": "Mercer",
        "preferred_name": "Lex",
        "professional_headline": "Senior Staff Frontend Architect",
        "email": "alex.mercer@example.com",
        "phone": "+1 (555) 019-2834",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "primary_title": "Frontend Architect",
        "secondary_titles": ["Staff Engineer", "UI Systems Lead"],
        "career_level": "senior",
        "industry": "Software Engineering",
        "years_of_experience": 8.5,
        "specializations": ["React", "Design Systems", "Web Performance"],
        "base_summary": "Seasoned frontend architect specializing in high-scale web platforms and design systems.",
    }
    create_res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["first_name"] == "Alex"
    assert data["last_name"] == "Mercer"
    assert data["preferred_name"] == "Lex"
    assert data["primary_title"] == "Frontend Architect"
    assert data["years_of_experience"] == 8.5
    assert len(data["specializations"]) == 3
    assert data["strength"]["completion_percentage"] > 0

    # 3. GET profile returns complete data
    get_res2 = await async_client.get("/api/v1/profile", headers=headers)
    assert get_res2.status_code == 200
    assert get_res2.json()["id"] == data["id"]
    assert get_res2.json()["first_name"] == "Alex"

    # 4. Duplicate creation -> 409 Conflict
    dup_res = await async_client.post("/api/v1/profile", json=payload, headers=headers)
    assert dup_res.status_code == 409


@pytest.mark.asyncio
async def test_update_and_delete_profile(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "update_delete@example.com")

    # Create profile
    create_res = await async_client.post(
        "/api/v1/profile",
        json={"first_name": "Taylor", "last_name": "Swift"},
        headers=headers,
    )
    assert create_res.status_code == 201

    # Update profile
    patch_res = await async_client.patch(
        "/api/v1/profile",
        json={"professional_headline": "Global Artist & Technologist", "years_of_experience": 15.0},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["professional_headline"] == "Global Artist & Technologist"
    assert patch_res.json()["years_of_experience"] == 15.0

    # Delete profile
    del_res = await async_client.delete("/api/v1/profile", headers=headers)
    assert del_res.status_code == 204

    # Subsequent GET returns 404
    get_res = await async_client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_links_crud(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "links@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Jordan"}, headers=headers)

    # 1. Add link
    link_res = await async_client.post(
        "/api/v1/profile/links",
        json={"type": "github", "label": "GitHub Profile", "url": "https://github.com/jordan", "order_index": 0},
        headers=headers,
    )
    assert link_res.status_code == 201
    link_id = link_res.json()["id"]

    # 2. Update link
    up_res = await async_client.patch(
        f"/api/v1/profile/links/{link_id}",
        json={"label": "Jordan's GitHub"},
        headers=headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["label"] == "Jordan's GitHub"

    # 3. Invalid URL validation
    invalid_res = await async_client.post(
        "/api/v1/profile/links",
        json={"type": "portfolio", "label": "Portfolio", "url": "ftp://invalid-scheme.com"},
        headers=headers,
    )
    assert invalid_res.status_code == 422

    # 4. Delete link
    del_res = await async_client.delete(f"/api/v1/profile/links/{link_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_work_experience_crud_and_metrics(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "experience@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Morgan"}, headers=headers)

    # 1. Create work experience with metrics
    exp_payload = {
        "company": "Northstar Labs",
        "position": "Staff Frontend Engineer",
        "employment_type": "full_time",
        "location": "Remote",
        "start_date": "2022-01",
        "end_date": "2024-06",
        "is_current": False,
        "description": "Led core web platform and design system architecture.",
        "responsibilities": ["Architected design tokens", "Mentored 6 engineers"],
        "achievements": [
            "Reduced bundle size by 42%",
            "Built token-driven design system adopted across 5 teams",
        ],
        "technologies": ["React", "TypeScript", "Tailwind CSS", "GraphQL"],
        "metrics": [
            {"value": 42, "unit": "percent", "description": "Bundle size reduction"},
            {"value": 5, "unit": "teams", "description": "Design system cross-team adoption"},
        ],
    }
    exp_res = await async_client.post("/api/v1/profile/experience", json=exp_payload, headers=headers)
    assert exp_res.status_code == 201
    exp_data = exp_res.json()
    assert exp_data["company"] == "Northstar Labs"
    assert len(exp_data["metrics"]) == 2
    assert exp_data["metrics"][0]["value"] == 42
    exp_id = exp_data["id"]

    # 2. Date validation: end_date preceding start_date
    invalid_exp = {
        "company": "Bad Dates Inc",
        "position": "Tester",
        "start_date": "2024-05",
        "end_date": "2022-01",
        "is_current": False,
    }
    inv_res = await async_client.post("/api/v1/profile/experience", json=invalid_exp, headers=headers)
    assert inv_res.status_code == 422

    # 3. Update experience
    up_res = await async_client.patch(
        f"/api/v1/profile/experience/{exp_id}",
        json={"is_current": True, "end_date": None},
        headers=headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["is_current"] is True

    # 4. Verify presence in main profile GET
    prof_res = await async_client.get("/api/v1/profile", headers=headers)
    assert len(prof_res.json()["experiences"]) == 1

    # 5. Delete experience
    del_res = await async_client.delete(f"/api/v1/profile/experience/{exp_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_skills_crud_and_duplicate_prevention(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "skills@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Devin"}, headers=headers)

    # 1. Add skill
    skill_res = await async_client.post(
        "/api/v1/profile/skills",
        json={
            "name": "TypeScript",
            "category": "programming_language",
            "proficiency": "expert",
            "years_of_experience": 6.0,
            "last_used": "2026",
            "evidence_references": ["Voyago repository", "Northstar frontend"],
        },
        headers=headers,
    )
    assert skill_res.status_code == 201
    skill_id = skill_res.json()["id"]

    # 2. Duplicate skill (case-insensitive) -> 409
    dup_res = await async_client.post(
        "/api/v1/profile/skills",
        json={"name": "typescript", "category": "programming_language"},
        headers=headers,
    )
    assert dup_res.status_code == 409

    # 3. Update skill
    up_res = await async_client.patch(
        f"/api/v1/profile/skills/{skill_id}",
        json={"proficiency": "advanced"},
        headers=headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["proficiency"] == "advanced"

    # 4. Delete skill
    del_res = await async_client.delete(f"/api/v1/profile/skills/{skill_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_projects_crud(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "projects@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Samantha"}, headers=headers)

    # 1. Create project
    proj_res = await async_client.post(
        "/api/v1/profile/projects",
        json={
            "name": "Voyago",
            "role": "Creator & Lead Developer",
            "description": "Real-time collaborative travel itinerary planner.",
            "problem": "Coordinating complex multi-stop itineraries across teams is chaotic.",
            "solution": "Built reactive canvas with optimistic UI and live operational transforms.",
            "technologies": ["Next.js", "Socket.IO", "PostgreSQL", "Redis"],
            "live_url": "https://voyago.app",
            "repository_url": "https://github.com/sam/voyago",
            "featured": True,
        },
        headers=headers,
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]
    assert proj_res.json()["featured"] is True

    # 2. Update project
    up_res = await async_client.patch(
        f"/api/v1/profile/projects/{proj_id}",
        json={"team_size": 4},
        headers=headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["team_size"] == 4

    # 3. Delete project
    del_res = await async_client.delete(f"/api/v1/profile/projects/{proj_id}", headers=headers)
    assert del_res.status_code == 204


@pytest.mark.asyncio
async def test_education_certifications_achievements_languages(async_client: AsyncClient):
    headers = await get_auth_headers(async_client, "full_sections@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "Elena"}, headers=headers)

    # Education
    edu_res = await async_client.post(
        "/api/v1/profile/education",
        json={
            "institution": "University of California, Berkeley",
            "degree": "B.S. Electrical Engineering & Computer Science",
            "field_of_study": "Computer Science",
            "start_date": "2016",
            "end_date": "2020",
            "grade": "3.85 GPA",
            "achievements": ["Dean's Honor List", "Undergraduate Research Fellow"],
        },
        headers=headers,
    )
    assert edu_res.status_code == 201
    edu_id = edu_res.json()["id"]

    # Certification
    cert_res = await async_client.post(
        "/api/v1/profile/certifications",
        json={
            "name": "AWS Certified Solutions Architect",
            "issuer": "Amazon Web Services",
            "issue_date": "2023-05",
            "credential_url": "https://aws.amazon.com/verify/12345",
            "skills": ["AWS", "Cloud Architecture"],
        },
        headers=headers,
    )
    assert cert_res.status_code == 201
    cert_id = cert_res.json()["id"]

    # Achievement
    ach_res = await async_client.post(
        "/api/v1/profile/achievements",
        json={
            "title": "1st Place Winner - HackMIT",
            "issuer": "MIT",
            "date": "2023-09",
            "category": "hackathon",
            "evidence_url": "https://hackmit.org/winners/2023",
        },
        headers=headers,
    )
    assert ach_res.status_code == 201
    ach_id = ach_res.json()["id"]

    # Language
    lang_res = await async_client.post(
        "/api/v1/profile/languages",
        json={"name": "English", "proficiency": "native"},
        headers=headers,
    )
    assert lang_res.status_code == 201
    lang_id = lang_res.json()["id"]

    # Preferences
    pref_res = await async_client.put(
        "/api/v1/profile/preferences",
        json={
            "target_roles": ["Senior Staff Engineer", "Principal Architect"],
            "remote_preference": "remote",
            "availability_status": "open_to_opportunities",
            "notice_period_days": 30,
        },
        headers=headers,
    )
    assert pref_res.status_code == 200
    assert pref_res.json()["notice_period_days"] == 30

    # Verify complete aggregated profile
    full_prof = await async_client.get("/api/v1/profile", headers=headers)
    assert full_prof.status_code == 200
    data = full_prof.json()
    assert len(data["education"]) == 1
    assert len(data["certifications"]) == 1
    assert len(data["achievements"]) == 1
    assert len(data["languages"]) == 1
    assert data["career_preferences"]["remote_preference"] == "remote"

    # Strength check
    strength_res = await async_client.get("/api/v1/profile/strength", headers=headers)
    assert strength_res.status_code == 200
    assert strength_res.json()["sections_breakdown"]["education"] is True
    assert strength_res.json()["sections_breakdown"]["languages"] is True


@pytest.mark.asyncio
async def test_cross_user_isolation_and_security(async_client: AsyncClient):
    # Setup User A
    headers_a = await get_auth_headers(async_client, "user_a@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "UserA"}, headers=headers_a)
    link_a = await async_client.post(
        "/api/v1/profile/links",
        json={"type": "github", "label": "User A Github", "url": "https://github.com/usera"},
        headers=headers_a,
    )
    link_a_id = link_a.json()["id"]

    # Setup User B
    headers_b = await get_auth_headers(async_client, "user_b@example.com")
    await async_client.post("/api/v1/profile", json={"first_name": "UserB"}, headers=headers_b)

    # 1. User B cannot see User A's data via GET /api/v1/profile
    prof_b = await async_client.get("/api/v1/profile", headers=headers_b)
    assert prof_b.json()["first_name"] == "UserB"
    assert len(prof_b.json()["links"]) == 0

    # 2. User B cannot patch User A's link ID -> 404 (isolated to User B's profile)
    patch_b = await async_client.patch(
        f"/api/v1/profile/links/{link_a_id}",
        json={"label": "Malicious Hijack"},
        headers=headers_b,
    )
    assert patch_b.status_code == 404

    # 3. User B cannot delete User A's link ID -> 404
    del_b = await async_client.delete(f"/api/v1/profile/links/{link_a_id}", headers=headers_b)
    assert del_b.status_code == 404

    # 4. User A's link is intact
    prof_a = await async_client.get("/api/v1/profile", headers=headers_a)
    assert len(prof_a.json()["links"]) == 1
    assert prof_a.json()["links"][0]["label"] == "User A Github"
