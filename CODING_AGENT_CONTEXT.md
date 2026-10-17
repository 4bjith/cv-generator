# AI CV Maker — Coding Agent Context

## 1. Mission

Build an AI-powered job application assistant.

The application maintains a structured, evidence-backed professional profile for a candidate and uses Google Gemini to analyze jobs and generate tailored CVs, cover emails, cover letters, and interview preparation.

The product is NOT merely an AI resume generator.

The core architecture is:

```text
Candidate Knowledge Base
        +
Job Intelligence
        +
Evidence-based Matching
        +
AI Generation
        +
Application Tracking
```

---

## 2. Non-Negotiable Rules

### Rule A — Never fabricate candidate information

The system must never invent:

- Experience
- Skills
- Technologies
- Projects
- Achievements
- Education
- Certifications
- Metrics
- Job titles
- Responsibilities

If information is missing, ask the user.

### Rule B — Evidence-backed generation

Generated CV content must be based on information stored in the Candidate Knowledge Base and associated evidence.

### Rule C — AI is not the database

The database is the source of truth.

Gemini is an intelligence layer used for extraction, classification, reasoning, matching, and generation.

### Rule D — User remains in control

AI-generated content must be editable.

Never silently modify permanent candidate information.

### Rule E — Provider abstraction

Do not couple application business logic directly to Gemini SDK calls.

Use an internal AI provider interface.

---

# 3. Technology Decisions

## Frontend

```text
Next.js
TypeScript
App Router
Tailwind CSS
shadcn/ui
TanStack Query
React Hook Form
Zod
```

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
Alembic
Pytest
```

## Data

```text
PostgreSQL
pgvector
Redis
S3-compatible storage
```

## AI

```text
Google Gemini
```

Gemini model names must be environment-configurable.

Do not hard-code model names throughout the codebase.

Example:

```env
GEMINI_API_KEY=
GEMINI_TEXT_MODEL=
GEMINI_VISION_MODEL=
GEMINI_EMBEDDING_MODEL=
```

---

# 4. Recommended Repository Structure

```text
ai-cv-maker/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   ├── types/
│   └── public/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── ai/
│   │   ├── workers/
│   │   └── utils/
│   │
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── README.md
└── docs/
```

---

# 5. Backend Architecture

Use layered architecture.

```text
API Layer
   ↓
Service Layer
   ↓
Repository Layer
   ↓
Database
```

AI should be a service dependency rather than embedded directly inside route handlers.

Bad:

```python
@app.post("/generate-cv")
async def generate_cv():
    # huge Gemini prompt
    # DB queries
    # business logic
    # PDF generation
```

Preferred:

```python
@app.post("/generate-cv")
async def generate_cv(request):
    return await cv_service.generate(request)
```

---

# 6. AI Provider Interface

Create an abstraction similar to:

```python
class AIProvider(Protocol):
    async def generate_text(...): ...
    async def generate_structured(...): ...
    async def analyze_image(...): ...
    async def generate_embedding(...): ...
```

Then implement:

```text
AIProvider
    └── GeminiProvider
```

Future providers should be replaceable without rewriting application logic.

---

# 7. AI Structured Output

Prefer structured output for:

- CV parsing
- Job analysis
- Skill extraction
- Project analysis
- Requirement matching
- Clarification questions

Validate all AI output with Pydantic schemas.

Never trust raw LLM output.

Pipeline:

```text
Gemini
  ↓
JSON/structured response
  ↓
Pydantic validation
  ↓
Business validation
  ↓
Database
```

---

# 8. Candidate Knowledge Base

The candidate profile is the central domain model.

Major objects:

```text
CandidateProfile
Experience
Education
Skill
Project
Certification
Achievement
Evidence
```

Every generated claim should ideally have evidence.

Example:

```text
Skill: Socket.IO

Evidence:
Project: Voyago
Source: GitHub
Observed: Socket.IO dependency and implementation
```

---

# 9. Evidence States

Use explicit evidence states:

```text
OBSERVED
USER_CONFIRMED
INFERRED
UNKNOWN
```

Only OBSERVED and USER_CONFIRMED information should normally be treated as safe factual CV material.

INFERRED information requires careful validation or user confirmation.

UNKNOWN must never become a factual claim.

---

# 10. CV Pipeline

```text
Candidate Knowledge Base
        +
Job Analysis
        +
Requirement Matches
        ↓
Candidate Evidence Selection
        ↓
CV Content Generation
        ↓
Pydantic CV Schema
        ↓
Validation
        ↓
Template Rendering
        ↓
PDF/DOCX
```

Do not generate PDFs directly from Gemini output.

---

# 11. Job Analysis Pipeline

```text
Input
  |
  +-- Text
  +-- Screenshot
  +-- PDF
  +-- DOCX
  +-- URL
  |
  v
Content Extraction
  |
  v
Gemini Job Analyzer
  |
  v
Structured Job
  |
  v
Validation
  |
  v
Database
```

---

# 12. Matching Pipeline

```text
Job Requirements
        |
        v
Requirement Matcher
        |
        +--> Candidate Skills
        +--> Experience
        +--> Projects
        +--> Evidence
        |
        v
RequirementMatch
```

Each requirement gets:

```text
STRONG
PARTIAL
WEAK
NONE
UNKNOWN
```

Do not convert NONE or UNKNOWN into a positive match.

---

# 13. Clarification Pipeline

```text
Requirement
      ↓
No reliable evidence
      ↓
Clarification Engine
      ↓
Question
      ↓
User Answer
      ↓
Temporary Application Context
      ↓
Optional profile update after confirmation
```

Do not automatically add temporary answers to permanent profile data.

---

# 14. GitHub Analyzer

The GitHub analyzer should be selective.

Retrieve useful repository information such as:

```text
README
package.json
requirements.txt
pyproject.toml
source tree
relevant source files
tests
deployment files
```

Do not automatically ingest every file from every repository.

For large repositories:

```text
Repository metadata
      ↓
Repository classification
      ↓
Relevant file selection
      ↓
Gemini analysis
```

---

# 15. GitHub Evidence Rules

The analyzer can state:

```text
Observed:
Repository uses React.

Observed:
Repository contains Socket.IO implementation.

Potential:
Candidate may have implemented real-time functionality.

Requires confirmation:
Candidate's exact personal contribution if repository is collaborative.
```

Do not convert "repository contains X" into "candidate personally implemented X" without evidence.

---

# 16. Document Processing

Use:

```text
PDF     → PyMuPDF
DOCX    → python-docx
Images  → OCR / Gemini vision
TXT     → native parser
```

Uploaded files should be validated for:

- MIME type
- Extension
- Size
- Malware/security constraints

---

# 17. Database Principles

Use PostgreSQL.

Use foreign keys and constraints.

Use migrations through Alembic.

Do not put arbitrary unvalidated AI JSON blobs everywhere.

Important AI-generated objects should have explicit schemas.

Use JSONB only where flexibility is genuinely useful.

Use pgvector for semantic retrieval.

---

# 18. Background Jobs

Use Redis-backed workers for expensive operations.

Examples:

```text
parse_cv
analyze_github_repository
generate_embeddings
analyze_job
generate_cv
generate_cover_letter
generate_interview
render_pdf
```

HTTP requests should not wait for long-running jobs.

Use job status:

```text
QUEUED
PROCESSING
COMPLETED
FAILED
```

---

# 19. Frontend Principles

Use server/client boundaries intentionally.

Use TanStack Query for server state.

Use React Hook Form + Zod for forms.

Do not duplicate backend validation rules blindly; frontend validation is for UX, backend validation is authoritative.

---

# 20. UI Principles

The UI should feel like a professional career/productivity application.

Prioritize:

- Clean layouts
- Clear status
- Progressive disclosure
- Editable AI output
- Evidence visibility
- Application-centric workflows

Avoid making every screen look like a chatbot.

AI should be integrated into workflows rather than represented only as a chat interface.

---

# 21. Core User Journey

The primary happy path is:

```text
Register
 ↓
Onboarding
 ↓
Upload old CV
 ↓
Review extracted profile
 ↓
Connect GitHub
 ↓
Analyze projects
 ↓
Paste/upload job
 ↓
Analyze job
 ↓
Review match
 ↓
Answer clarification questions
 ↓
Generate CV
 ↓
Review/edit CV
 ↓
Generate application email
 ↓
Generate interview preparation
 ↓
Create application
 ↓
Track status
```

---

# 22. API Conventions

Use:

```text
/api/...
```

Use RESTful resources.

Use consistent response/error formats.

Example:

```json
{
  "success": true,
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request"
  }
}
```

Use HTTP status codes correctly.

---

# 23. Authentication and Authorization

Every authenticated resource must verify ownership.

Example:

```text
GET /api/applications/123
```

must verify that application 123 belongs to the authenticated user.

Never trust a user ID supplied by the frontend.

---

# 24. Secrets

Never expose:

```text
GEMINI_API_KEY
DATABASE_URL
JWT_SECRET
GITHUB_CLIENT_SECRET
S3_SECRET
```

to the frontend.

Use environment variables/secrets management.

Provide:

```text
.env.example
```

without real secrets.

---

# 25. AI Prompt Organization

Do not put giant prompts inside route handlers.

Use:

```text
backend/app/ai/prompts/

profile/
job/
github/
matching/
cv/
cover_email/
interview/
```

Prompts should have:

- System instructions
- Input schema
- Output schema
- Evidence rules
- Examples where useful

---

# 26. AI Cost Control

Avoid unnecessary Gemini calls.

Use deterministic code for:

- File validation
- Date parsing
- Basic keyword matching
- Database operations
- Template rendering

Use Gemini when reasoning or language understanding is actually required.

Cache reusable analysis where appropriate.

---

# 27. AI Failure Handling

Gemini may fail, timeout, return invalid output, or hit rate limits.

Implement:

- Timeout
- Retry with backoff
- Schema validation
- Error state
- User-visible status
- Job retry
- Logging
- Provider error normalization

Never silently return fabricated fallback content.

---

# 28. Application State Machine

Recommended status flow:

```text
SAVED
  ↓
APPLIED
  ↓
SCREENING
  ↓
INTERVIEW
  ↓
TECHNICAL_ROUND
  ↓
FINAL_ROUND
  ↓
OFFER
```

Alternative terminal states:

```text
REJECTED
WITHDRAWN
ARCHIVED
```

Users may manually change status where appropriate.

---

# 29. Document Versioning

Generated documents must be immutable versions.

Do not overwrite old CVs.

Example:

```text
CV v1
CV v2
CV v3
```

Each version should record:

- Candidate profile snapshot/version
- Job snapshot/version
- Prompt/model metadata where appropriate
- Created timestamp
- Template
- Generated content

---

# 30. Auditability

For important AI-generated information, retain enough metadata to explain:

- Which job was used
- Which candidate information was used
- Which model generated it
- When it was generated
- Which document version was created

Do not store unnecessary sensitive prompt content.

---

# 31. Security Checklist

Before production:

```text
[ ] Authentication
[ ] Authorization
[ ] Rate limiting
[ ] Input validation
[ ] File validation
[ ] Secure object storage
[ ] Signed URLs
[ ] Secret management
[ ] SQL injection protection
[ ] XSS protection
[ ] CSRF strategy
[ ] OAuth token protection
[ ] Logging redaction
[ ] Account deletion
[ ] Data export
```

---

# 32. Development Order

Implement in this order:

### Step 1

Project scaffolding.

### Step 2

Docker + PostgreSQL + Redis.

### Step 3

Authentication.

### Step 4

Candidate profile database and APIs.

### Step 5

CV upload and parser.

### Step 6

Gemini provider abstraction.

### Step 7

Gemini CV/profile extraction.

### Step 8

Profile review UI.

### Step 9

GitHub OAuth/API.

### Step 10

GitHub project analyzer.

### Step 11

Job input and analysis.

### Step 12

Requirement matching.

### Step 13

Clarification system.

### Step 14

CV generation.

### Step 15

CV templates/PDF.

### Step 16

Cover email/letter.

### Step 17

Application tracker.

### Step 18

Interview preparation.

### Step 19

Testing/evaluation.

### Step 20

Production deployment.

---

# 33. Coding Agent Behavior

When implementing the system:

1. Read this context before modifying architecture.
2. Inspect the existing code before creating duplicate modules.
3. Keep frontend and backend responsibilities separate.
4. Follow existing project conventions.
5. Do not introduce a new dependency if an existing dependency already solves the problem.
6. Keep functions small and testable.
7. Use typed schemas.
8. Validate external and AI-generated data.
9. Do not hard-code secrets.
10. Do not hard-code Gemini model names.
11. Write tests for important business logic.
12. Do not silently change database schema without an Alembic migration.
13. Do not remove existing functionality without explicit instruction.
14. Prefer incremental implementation over large speculative rewrites.
15. Explain architectural changes before making significant changes.
16. After completing any feature, update the root `memory.md` with the feature status, files changed, validation performed, and remaining follow-up work.
17. Before changing an existing feature or its behavior, request and receive explicit user permission. Documentation-only maintenance requested by the user is exempt from this permission requirement.
18. When installing packages, prefer the latest stable versions compatible with the current runtime and framework; verify versions from the official package registry or documentation, avoid canary releases unless requested, and record important version decisions in `memory.md`.

---

# 34. Definition of Done for Each Feature

A feature is not complete merely because the UI works.

A feature should include:

```text
Backend API
Database model/migration if required
Pydantic schema
Business/service logic
Frontend UI
Loading state
Error state
Validation
Authorization
Tests
Documentation where appropriate
```

For AI features additionally require:

```text
Prompt
Structured output schema
AI validation
Failure handling
Evidence rules
Evaluation case
```

---

# 35. Current Priority

Build the MVP first.

Priority order:

```text
P0
Authentication
Candidate profile
CV import
Candidate Knowledge Base

P1
GitHub integration
Job analysis
Requirement matching
Clarification engine

P2
CV generation
ATS analysis
Cover email
Application tracker

P3
Interview preparation
Advanced templates
Analytics

Future
Browser extension
Job discovery
Application automation
```

Do not build automatic job application submission in the initial MVP.

---

# 36. Final Architecture Principle

The product should behave like:

```text
                 USER
                  |
                  v
        Candidate Knowledge Base
                  |
                  v
            Job Intelligence
                  |
                  v
         Evidence-based Matcher
                  |
          +-------+--------+
          |                |
          v                v
    Missing Evidence    Existing Evidence
          |                |
          v                v
      Ask User        Generate Content
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
            CV       Cover Email    Interview Prep
             |
             v
       Application Tracker
```

The central product differentiator is not simply "Gemini generates a CV."

It is:

**Build a persistent, evidence-backed understanding of the candidate, understand each job, and generate application materials specifically from the intersection of verified candidate evidence and job requirements.**
