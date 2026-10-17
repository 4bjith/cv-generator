# cv-generator

AI-powered CV maker and job application assistant that maintains an evidence-backed professional candidate profile, analyzes target jobs, extracts requirements, performs evidence-grounded matching, and generates tailored, version-isolated CVs.

## Architecture

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Vanilla CSS design system, Phosphor Icons, TanStack Query v5, Axios.
- **Backend**: FastAPI, Python 3.12+, Pydantic v2, SQLAlchemy 2 (async), Alembic, ReportLab Platypus (PDF), python-docx (Word DOCX).
- **Database**: PostgreSQL with Alembic migrations.

## Core Features

- **Candidate Knowledge Base**: Comprehensive career data model with normalized entities (skills, work experience, projects, education, certifications, and links).
- **Candidate Evidence System**: Traceable proof records (GitHub repositories, PRs, certificates, URLs, documents) linked to candidate claims.
- **Job Description Intelligence**: Full CRUD target job management, employment type capture, modular requirement extraction pipeline classifying mandatory vs. preferred requirements, seniority, categories, and keywords.
- **Evidence-Grounded Matching**: Non-hallucinatory comparison against candidate evidence records, detecting supported, partial, unverified, and missing qualifications with explicit gap distinction (`absent_from_profile`, `unverified_claim`, `skill_gap`).
- **CV Versioning & Snapshot Isolation**: Point-in-time immutable CV snapshots derived from the candidate profile without mutating the master record.
- **Template Design System**: 6 production-grade, visually distinct CV templates:
  - *Modern Professional*: Corporate single-column layout with clean hierarchy and accent bars.
  - *Classic Executive*: Formal serif layout with double rules and leadership focus.
  - *ATS-Friendly Minimal*: High-contrast linear layout optimized for applicant tracking systems.
  - *Technical / Software Developer*: Categorized technical skill matrix with monospace tags and system stacks.
  - *Contemporary Two-Column*: Asymmetric sidebar layout with separate summary and experience columns.
  - *Academic / Research*: Scholarly serif layout with education-first hierarchy, publications, and grants.
- **Production-Quality Export**:
  - High-resolution, searchable vector PDF generation via ReportLab (A4 and US Letter, configurable spacing densities, multi-page numbering).
  - Genuine Microsoft Word (.docx) generation with standard heading styles, bullet lists, and hyperlinking.

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to access the application.

## Testing

```bash
# Backend pytest suite (76 tests)
cd backend
.\.venv\Scripts\pytest -q

# Frontend vitest suite (77 tests)
cd frontend
npm test -- --run
```
