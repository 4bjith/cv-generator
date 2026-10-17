"""Automated test suite for CV PDF and DOCX export pipeline."""

import io
import uuid
import zipfile
import pytest
from httpx import AsyncClient
from pypdf import PdfReader

from app.schemas.cv import CVContentSnapshot
from app.services.export import (
    ALL_SUPPORTED_TEMPLATES,
    generate_cv_docx,
    generate_cv_pdf,
    get_sanitized_export_filename,
)


async def get_auth_headers(client: AsyncClient, email: str = "export_user@example.com") -> dict:
    """Helper to register a user and obtain authorization header."""
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "Export Test User",
        },
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def create_test_cv_version(client: AsyncClient, headers: dict) -> dict:
    """Helper to initialize a complete candidate profile and create a CV version."""
    # 1. Setup profile
    profile_payload = {
        "first_name": "Marcus",
        "last_name": "Aurelius",
        "professional_headline": "Senior Staff Architect & Engineering Director",
        "email": "marcus.aurelius@example.com",
        "city": "Rome",
        "country": "Italy",
        "base_summary": "Pioneering distributed resilient architectures, high-performance team leadership, and strategic execution.",
    }
    prof_resp = await client.post("/api/v1/profile", json=profile_payload, headers=headers)
    assert prof_resp.status_code == 201

    # Add experience
    await client.post(
        "/api/v1/profile/experience",
        json={
            "company": "Imperial Systems",
            "position": "Director of Architecture",
            "start_date": "2020-01-01",
            "is_current": True,
            "description": "Overseeing empire-wide distributed infrastructure.",
            "responsibilities": ["Led architecture for 120 engineers", "Reduced downtime to 99.999%"],
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Kafka"],
        },
        headers=headers,
    )

    # Add skill
    await client.post(
        "/api/v1/profile/skills",
        json={
            "name": "Distributed Systems",
            "category": "Architecture",
            "proficiency": "expert",
            "keywords": ["Consensus", "Event Sourcing", "Microservices"],
        },
        headers=headers,
    )

    # 2. Create CV version
    cv_resp = await client.post(
        "/api/v1/cv/versions",
        json={"name": "Marcus Executive Master CV"},
        headers=headers,
    )
    assert cv_resp.status_code == 201
    return cv_resp.json()


# ==============================================================================
# Endpoint & Authentication Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_export_pdf_endpoint_success(async_client: AsyncClient):
    """Test GET /cv/versions/{id}/export/pdf generates valid PDF."""
    headers = await get_auth_headers(async_client, "pdf_test@example.com")
    cv_ver = await create_test_cv_version(async_client, headers)
    version_id = cv_ver["id"]

    res = await async_client.get(f"/api/v1/cv/versions/{version_id}/export/pdf", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in res.headers["content-disposition"]
    assert "Marcus_Aurelius_CV.pdf" in res.headers["content-disposition"]

    # Verify PDF content
    pdf_bytes = res.content
    assert pdf_bytes.startswith(b"%PDF-")
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1
    extracted = "".join(p.extract_text() or "" for p in reader.pages)
    assert "Marcus Aurelius" in extracted
    assert "Imperial Systems" in extracted


@pytest.mark.asyncio
async def test_export_docx_endpoint_success(async_client: AsyncClient):
    """Test GET /cv/versions/{id}/export/docx generates valid DOCX."""
    headers = await get_auth_headers(async_client, "docx_test@example.com")
    cv_ver = await create_test_cv_version(async_client, headers)
    version_id = cv_ver["id"]

    res = await async_client.get(f"/api/v1/cv/versions/{version_id}/export/docx", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "attachment; filename=" in res.headers["content-disposition"]
    assert "Marcus_Aurelius_CV.docx" in res.headers["content-disposition"]

    # Verify DOCX zip structure
    docx_bytes = res.content
    zf = zipfile.ZipFile(io.BytesIO(docx_bytes))
    namelist = zf.namelist()
    assert "word/document.xml" in namelist
    assert "[Content_Types].xml" in namelist
    assert "_rels/.rels" in namelist

    doc_xml = zf.read("word/document.xml").decode("utf-8")
    assert "Marcus Aurelius" in doc_xml
    assert "Imperial Systems" in doc_xml


@pytest.mark.asyncio
async def test_export_endpoints_require_auth(async_client: AsyncClient):
    """Test unauthenticated export requests return 401."""
    random_id = uuid.uuid4()
    pdf_res = await async_client.get(f"/api/v1/cv/versions/{random_id}/export/pdf")
    assert pdf_res.status_code == 401

    docx_res = await async_client.get(f"/api/v1/cv/versions/{random_id}/export/docx")
    assert docx_res.status_code == 401


@pytest.mark.asyncio
async def test_export_cross_user_isolation(async_client: AsyncClient):
    """Test User B cannot export User A's CV version."""
    headers_a = await get_auth_headers(async_client, "user_a_export@example.com")
    headers_b = await get_auth_headers(async_client, "user_b_export@example.com")

    cv_ver = await create_test_cv_version(async_client, headers_a)
    version_id = cv_ver["id"]

    # User B attempts PDF export
    res_pdf = await async_client.get(f"/api/v1/cv/versions/{version_id}/export/pdf", headers=headers_b)
    assert res_pdf.status_code == 404

    # User B attempts DOCX export
    res_docx = await async_client.get(f"/api/v1/cv/versions/{version_id}/export/docx", headers=headers_b)
    assert res_docx.status_code == 404


@pytest.mark.asyncio
async def test_export_with_query_param_overrides(async_client: AsyncClient):
    """Test export endpoints with template, page_size, and spacing query overrides."""
    headers = await get_auth_headers(async_client, "overrides_user@example.com")
    cv_ver = await create_test_cv_version(async_client, headers)
    version_id = cv_ver["id"]

    for t in ALL_SUPPORTED_TEMPLATES:
        pdf_res = await async_client.get(
            f"/api/v1/cv/versions/{version_id}/export/pdf?template={t}&page_size=letter&spacing=compact",
            headers=headers,
        )
        assert pdf_res.status_code == 200
        assert pdf_res.content.startswith(b"%PDF-")

        docx_res = await async_client.get(
            f"/api/v1/cv/versions/{version_id}/export/docx?template={t}&page_size=letter&spacing=compact",
            headers=headers,
        )
        assert docx_res.status_code == 200
        zf = zipfile.ZipFile(io.BytesIO(docx_res.content))
        assert "word/document.xml" in zf.namelist()


# ==============================================================================
# Unit & Engine Tests: All 6 Templates, Multi-Page, Resilience
# ==============================================================================

def test_all_six_templates_pdf_and_docx():
    """Verify that all six launch templates produce valid PDF and DOCX files."""
    snapshot = CVContentSnapshot.model_validate({
        "basics": {
            "name": "Sarah Connor",
            "label": "Defense Systems Analyst",
            "email": "sarah@resistance.org",
            "phone": "+1 555 0199",
            "summary": "Expert in threat modelling, robotics defenses, and resilient infrastructure.",
        },
        "work": [
            {
                "company": "Cyberdyne Systems",
                "position": "Security Auditor",
                "start_date": "2021-01-01",
                "end_date": "2023-12-31",
                "highlights": ["Audited neural net processor protocols", "Prevented rogue automation deployment"],
                "technologies": ["Assembly", "C++", "Cryptographic Verification"],
            }
        ],
        "skills": [
            {"name": "Security", "keywords": ["Penetration Testing", "Threat Modeling"]},
            {"name": "Tactical Operations", "keywords": ["Survival", "Reconnaissance"]},
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "B.S. in Computer Science",
                "start_date": "2016-09-01",
                "end_date": "2020-06-01",
            }
        ],
        "certificates": [
            {"name": "CISSP - Certified Information Systems Security Professional", "issuer": "ISC2", "date": "2022-04"}
        ],
        "awards": [
            {"title": "Excellence in Counter-Cyber Defense", "awarder": "National Cyber Consortium", "date": "2023-10"}
        ],
        "languages": [
            {"language": "English", "fluency": "Native"},
            {"language": "Spanish", "fluency": "Professional"},
        ],
        "presentation": {"template": "modern-professional"},
    })

    for template_id in ALL_SUPPORTED_TEMPLATES:
        # Test PDF
        pdf_bytes = generate_cv_pdf(snapshot, overrides={"template": template_id})
        assert pdf_bytes.startswith(b"%PDF-"), f"Failed PDF header for template {template_id}"
        reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(reader.pages) >= 1
        pdf_text = "".join(p.extract_text() or "" for p in reader.pages)
        assert "Sarah Connor" in pdf_text
        assert "Cyberdyne Systems" in pdf_text
        assert "CISSP" in pdf_text

        # Test DOCX
        docx_bytes = generate_cv_docx(snapshot, overrides={"template": template_id})
        zf = zipfile.ZipFile(io.BytesIO(docx_bytes))
        assert "word/document.xml" in zf.namelist(), f"Failed DOCX zip for template {template_id}"
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        assert "Sarah Connor" in doc_xml
        assert "Cyberdyne Systems" in doc_xml


def test_page_sizes_and_dimensions():
    """Verify A4 and US Letter page sizes set appropriate dimensions."""
    snapshot = CVContentSnapshot.model_validate({
        "basics": {"name": "Dimension Test User", "email": "dim@example.com"},
        "work": [{"company": "Tech Corp", "position": "Developer"}],
    })

    # A4: 595.27 x 841.89 points
    pdf_a4 = generate_cv_pdf(snapshot, overrides={"page_size": "a4"})
    reader_a4 = PdfReader(io.BytesIO(pdf_a4))
    box_a4 = reader_a4.pages[0].mediabox
    assert round(float(box_a4.width)) == 595
    assert round(float(box_a4.height)) == 842

    # Letter: 612 x 792 points
    pdf_letter = generate_cv_pdf(snapshot, overrides={"page_size": "letter"})
    reader_letter = PdfReader(io.BytesIO(pdf_letter))
    box_letter = reader_letter.pages[0].mediabox
    assert round(float(box_letter.width)) == 612
    assert round(float(box_letter.height)) == 792


def test_multi_page_content_flow():
    """Verify long descriptions, many work experiences, and skills flow cleanly to multiple pages."""
    work_list = []
    for i in range(12):
        work_list.append({
            "company": f"Enterprise Scale Corp {i}",
            "position": f"Lead Distributed Systems Architect {i}",
            "start_date": f"201{i % 10}-01-01",
            "end_date": f"201{i % 10}-12-31",
            "summary": "Spearheaded organizational transformation, replatforming multi-tier services into cloud-native microservices.",
            "highlights": [
                f"Led migration of {100 + i * 20} microservices to Kubernetes with zero downtime",
                "Reduced infrastructure compute expenses by $2.4M annually through dynamic autoscaling",
                "Mentored senior engineering staff and authored enterprise architecture standards",
            ],
            "technologies": ["Kubernetes", "Golang", "PostgreSQL", "Kafka", "Terraform", "Prometheus"],
        })

    snapshot = CVContentSnapshot.model_validate({
        "basics": {
            "name": "Dr. Alexander Cross",
            "label": "VP of Infrastructure Engineering",
            "email": "alex.cross@example.com",
            "summary": "Executive engineering leader with 20+ years building hyperscale systems.",
        },
        "work": work_list,
        "education": [
            {"institution": "MIT", "degree": "M.S. in Electrical Engineering & Computer Science"}
        ],
    })

    pdf_bytes = generate_cv_pdf(snapshot)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) > 1, f"Expected multi-page PDF, got {len(reader.pages)}"
    full_text = "".join(p.extract_text() or "" for p in reader.pages)
    assert "Enterprise Scale Corp 0" in full_text
    assert "Enterprise Scale Corp 11" in full_text

    docx_bytes = generate_cv_docx(snapshot)
    zf = zipfile.ZipFile(io.BytesIO(docx_bytes))
    doc_xml = zf.read("word/document.xml").decode("utf-8")
    assert "Enterprise Scale Corp 11" in doc_xml


def test_malformed_and_missing_content_resilience():
    """Verify exporter handles missing fields, empty snapshot, and None gracefully."""
    empty_snapshot = CVContentSnapshot.model_validate({})

    # Must not raise exceptions
    pdf_bytes = generate_cv_pdf(empty_snapshot)
    assert pdf_bytes.startswith(b"%PDF-")

    docx_bytes = generate_cv_docx(empty_snapshot)
    assert len(docx_bytes) > 1000

    # Bare basics
    minimal_snapshot = CVContentSnapshot.model_validate({"basics": {"name": ""}})
    pdf_min = generate_cv_pdf(minimal_snapshot)
    assert pdf_min.startswith(b"%PDF-")

    docx_min = generate_cv_docx(minimal_snapshot)
    assert len(docx_min) > 1000


def test_filename_sanitization():
    """Test export filename sanitization."""
    assert get_sanitized_export_filename("John Doe", "pdf") == "John_Doe_CV.pdf"
    assert get_sanitized_export_filename("Dr. Jane O'Connor, Ph.D.", "docx") == "Dr_Jane_OConnor_PhD_CV.docx"
    assert get_sanitized_export_filename("   ", "pdf") == "CV_Document_CV.pdf"
