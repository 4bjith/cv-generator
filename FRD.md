# AI CV Maker — Functional Requirements Document (FRD)

**Version:** 1.0  
**Status:** Initial Product Specification  
**Primary AI Provider:** Google Gemini  
**Frontend:** Next.js + TypeScript  
**Backend:** Python + FastAPI  
**Database:** PostgreSQL + pgvector  
**Cache/Queue:** Redis  
**Storage:** S3-compatible object storage

---

## 1. Product Overview

### 1.1 Product Name

AI CV Maker

### 1.2 Product Purpose

AI CV Maker is an AI-powered job application assistant that maintains a structured professional profile for a candidate and uses that profile to create truthful, ATS-friendly, job-specific application materials.

The system accepts job descriptions from sources such as LinkedIn, Indeed, Naukri, company career pages, recruiters, screenshots, PDFs, DOCX files, or pasted text.

The system analyzes the job, compares its requirements against the candidate's verified professional evidence, asks the candidate for missing information when necessary, and generates:

- Tailored ATS-friendly CV/resume
- Application/cover email
- Optional cover letter
- Recruiter/LinkedIn message
- Interview preparation
- Application tracking information

The system must never fabricate experience, skills, education, projects, employment, achievements, or other candidate facts.

---

# 2. Product Goals

## 2.1 Primary Goals

1. Maintain a reusable structured candidate profile.
2. Import and understand an existing CV.
3. Import and analyze GitHub projects.
4. Accept job descriptions through multiple input methods.
5. Extract structured job requirements.
6. Match candidate evidence against job requirements.
7. Ask clarification questions when evidence is missing or ambiguous.
8. Generate job-specific ATS-friendly CVs.
9. Generate application emails and cover letters.
10. Generate interview preparation based on the actual job and candidate profile.
11. Track job applications and their status.
12. Preserve document versions and application history.

## 2.2 Non-Goals for MVP

The MVP will not:

- Automatically apply to jobs on third-party websites.
- Automatically bypass CAPTCHA or anti-bot systems.
- Scrape protected LinkedIn/Indeed/Naukri pages.
- Claim that a CV is guaranteed to pass an ATS.
- Invent candidate information.
- Automatically send applications without explicit user action.

---

# 3. Target Users

## 3.1 Primary User

Job seekers who want to:

- Maintain a professional profile.
- Tailor CVs for individual jobs.
- Reduce repetitive application work.
- Prepare for interviews.
- Track applications.

## 3.2 Future Users

- Students
- Fresh graduates
- Experienced professionals
- Career coaches
- Universities/career centers

---

# 4. Core Product Concept

The central concept is the **Candidate Knowledge Base**.

The uploaded CV must not be treated as the permanent source of truth.

Instead:

```text
CV
LinkedIn information
GitHub repositories
User-entered information
Projects
Experience
Education
Achievements
Certifications
        |
        v
Candidate Knowledge Base
        |
        v
Evidence-backed professional profile
```

Every generated document should be based on this structured profile.

---

# 5. High-Level System Architecture

```text
                         Next.js Frontend
                               |
                               v
                         FastAPI Backend
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
 Candidate Intelligence   Job Intelligence     Application Management
        |                      |
        +----------+-----------+
                   |
                   v
             AI Orchestration
                   |
       +-----------+------------+
       |           |            |
       v           v            v
    Gemini      Embeddings     Vision/OCR
       |
       v
 PostgreSQL + pgvector
       |
       +-------------+
       |             |
       v             v
     Redis        S3/R2
```

---

# 6. Technology Stack

## 6.1 Frontend

- Next.js
- TypeScript
- App Router
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod

## 6.2 Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- Pytest

## 6.3 Database

- PostgreSQL
- pgvector

## 6.4 AI

Primary provider:

- Google Gemini models

The AI layer must be implemented behind an internal provider abstraction so models can be changed without modifying business logic.

Example abstraction:

```text
AIProvider
├── generate_text()
├── generate_structured()
├── analyze_image()
├── generate_embedding()
└── count_tokens()
```

The initial implementation will use Gemini.

## 6.5 Infrastructure

- Docker
- Docker Compose for local development
- Redis
- S3-compatible object storage
- Vercel or equivalent for frontend
- AWS/Railway/Render/Fly.io or equivalent for backend

---

# 7. Functional Modules

## Module 1 — Authentication

Users must be able to:

- Register
- Login
- Logout
- Reset password
- Manage account
- Delete account

Future:

- Google OAuth
- GitHub OAuth

---

# 8. Module 2 — User Onboarding

The onboarding process should collect:

### Required

- Name
- Email
- Phone
- Location
- Current professional title/status
- Years of experience
- Existing CV

### Optional

- LinkedIn URL
- GitHub URL
- Portfolio URL
- Personal website
- Other professional profiles

### Onboarding workflow

```text
Create Account
      |
      v
Basic Information
      |
      v
Upload Existing CV
      |
      v
CV Parsing
      |
      v
Profile Extraction
      |
      v
GitHub Connection
      |
      v
Project Analysis
      |
      v
Profile Review
      |
      v
Candidate Knowledge Base
```

The user must be able to review and correct extracted information.

---

# 9. Module 3 — Candidate Knowledge Base

The profile should contain:

## Personal Information

- Name
- Email
- Phone
- Location
- Professional headline
- Summary

## Skills

Each skill should have:

- Name
- Category
- Self-reported level
- Evidence
- Source
- Confidence

Example:

```json
{
  "name": "React",
  "category": "frontend",
  "evidence": [
    {
      "source": "github",
      "project": "Voyago"
    }
  ]
}
```

## Experience

Store:

- Company
- Job title
- Start date
- End date
- Description
- Responsibilities
- Achievements
- Technologies
- Evidence source

## Projects

Store:

- Project name
- Description
- Role
- Technologies
- Features
- Responsibilities
- Results
- GitHub URL
- Live URL
- Evidence
- Visibility preference

## Education

Store:

- Institution
- Degree
- Field
- Start date
- End date
- GPA/grade if provided

## Certifications

Store:

- Name
- Issuer
- Date
- Credential URL

## Achievements

Store:

- Achievement
- Description
- Date
- Evidence

---

# 10. Evidence System

Every important candidate claim should be traceable to evidence.

Example:

```text
Claim:
"Built real-time ride tracking"

Evidence:
GitHub repository
Voyago
Socket.IO implementation
```

Evidence sources:

- User input
- Uploaded CV
- GitHub
- LinkedIn-provided data
- Portfolio
- Other connected source

The AI must not create unsupported claims.

---

# 11. Module 4 — CV Import and Parsing

Supported inputs:

- PDF
- DOCX
- TXT
- Images

Pipeline:

```text
Upload
  |
  v
File Validation
  |
  v
Text/OCR Extraction
  |
  v
Gemini Structured Extraction
  |
  v
Candidate Profile Draft
  |
  v
User Verification
  |
  v
Knowledge Base
```

The original file must be preserved.

---

# 12. Module 5 — GitHub Integration

## Authentication

Use GitHub OAuth where appropriate.

## Repository analysis

For selected repositories, retrieve:

- Repository name
- Description
- Languages
- README
- File structure
- package.json
- requirements.txt
- Relevant configuration files
- Public metadata
- Commit information where useful

Do not ingest an entire repository blindly.

The analyzer should prioritize:

- README
- package manifests
- source structure
- relevant implementation files
- tests
- deployment configuration

## GitHub Project Analyzer

The analyzer should determine:

- Technologies
- Architecture
- Major features
- Candidate's likely contribution where evidence exists
- APIs/integrations
- Database technologies
- Deployment information
- Testing
- Real-time features
- Relevant engineering practices

The system must distinguish:

```text
Observed
Inferred
User-confirmed
```

Only sufficiently supported information may be used as factual CV content.

---

# 13. Module 6 — Job Input

Supported job inputs:

1. Pasted text
2. Screenshot
3. PDF
4. DOCX
5. Image
6. Public URL where technically and legally accessible

The UI should provide:

```text
Paste Job Description
Upload Screenshot
Upload Document
Enter Job URL
```

---

# 14. Module 7 — Job Analysis

The job analyzer must extract:

- Job title
- Company
- Location
- Work mode
- Employment type
- Seniority
- Required skills
- Preferred skills
- Responsibilities
- Education requirements
- Experience requirements
- Certifications
- Domain knowledge
- Keywords
- Soft skills
- Technologies
- Salary information if available

Example structured output:

```json
{
  "title": "Frontend Developer",
  "seniority": "Junior",
  "required_skills": [
    "React",
    "JavaScript",
    "TypeScript"
  ],
  "preferred_skills": [
    "Next.js",
    "Jest"
  ]
}
```

---

# 15. Module 8 — Candidate/Job Matching

The matching engine compares:

```text
Job Requirements
        +
Candidate Evidence
        |
        v
Requirement Mapping
```

Each requirement should have a state:

- Strong evidence
- Partial evidence
- Weak evidence
- No evidence
- Unknown

Example:

```text
React        -> Strong evidence
TypeScript   -> Strong evidence
Next.js      -> Partial evidence
AWS          -> No evidence
Jest         -> Unknown
```

The system must not represent a missing skill as an existing skill.

---

# 16. Module 9 — Clarification Engine

When information is missing, the system generates questions.

Example:

```text
We found 2 requirements that need clarification:

1. The job requires AWS.
   Have you used AWS? If yes, where?

2. The job mentions Jest.
   Have you used Jest or another testing framework?
```

Questions must be:

- Specific
- Minimal
- Relevant to the current application
- Answerable by the user

Answers should optionally become part of the permanent Candidate Knowledge Base after user confirmation.

---

# 17. Module 10 — CV Generation

CV generation must happen in two stages.

## Stage 1 — Content

Generate structured CV JSON.

## Stage 2 — Rendering

Render structured content using a selected template.

```text
Candidate Knowledge
        +
Job Analysis
        +
Requirement Mapping
        |
        v
CV Content JSON
        |
        v
Template Renderer
        |
        v
PDF/DOCX
```

## CV requirements

- ATS-friendly
- Clean typography
- Standard section names
- No unnecessary graphics
- No fabricated information
- Job-relevant ordering
- Job-relevant project selection
- Appropriate keyword alignment
- Human-readable content

---

# 18. ATS Analysis

The system should provide an ATS compatibility report.

Possible checks:

- Required keyword coverage
- Skill coverage
- Standard section naming
- Contact information presence
- Formatting issues
- Excessive tables/graphics
- Unsupported symbols
- Missing job-critical information
- Date consistency
- Potential parsing issues

Do not claim guaranteed ATS success.

---

# 19. Module 11 — Cover Email

Generate a concise application email based on:

- Job
- Company
- Candidate
- Tailored CV
- Relevant projects

The email should include:

- Subject
- Greeting
- Application intent
- Relevant qualifications
- Relevant project/experience
- Closing
- Contact information where appropriate

---

# 20. Module 12 — Cover Letter

Optional longer document.

It should be generated from the same verified evidence used for the CV.

---

# 21. Module 13 — Recruiter Message

Generate short messages suitable for:

- LinkedIn
- Recruiter outreach
- Referral requests

The system should support multiple tone options.

---

# 22. Module 14 — Interview Preparation

Interview preparation must be job-specific.

Generate:

### Technical questions

Based on job requirements.

### Project questions

Based on projects included in the CV.

### Experience questions

Based on candidate experience.

### Behavioral questions

Based on the role.

### Company/job-specific questions

Based on available job information.

Each question may include:

- Question
- Why it may be asked
- Suggested answer structure
- Candidate evidence
- Follow-up questions

---

# 23. Module 15 — Application Tracker

Application statuses:

```text
Saved
Applied
Screening
Interview
Technical Round
Final Round
Offer
Rejected
Withdrawn
Archived
```

Each application should maintain:

- Company
- Position
- Job description
- Job URL
- Application date
- Status
- CV version
- Cover email version
- Cover letter version
- Interview preparation
- Notes
- Interview dates
- Follow-up dates
- Status history

---

# 24. Application Versioning

Every generated artifact should be versioned.

Example:

```text
Application #42

CV v1
CV v2
Cover Email v1
Cover Letter v1
Interview Prep v1
```

The user must be able to regenerate without destroying previous versions.

---

# 25. AI Architecture

The AI layer must be separated from business logic.

```text
app/ai/

provider/
    base.py
    gemini.py

prompts/
    profile_extraction/
    job_analysis/
    matching/
    cv_generation/
    cover_email/
    interview/

schemas/
    profile.py
    job.py
    cv.py

validators/
    hallucination.py
    evidence.py
```

Use structured output wherever possible.

---

# 26. Gemini Integration

Gemini is the primary model provider.

The system should support different Gemini models for different workloads.

Model selection must be configurable.

Example configuration:

```env
GEMINI_API_KEY=
GEMINI_TEXT_MODEL=
GEMINI_VISION_MODEL=
GEMINI_EMBEDDING_MODEL=
```

Do not hard-code model names throughout the application.

The provider layer should expose a stable interface.

---

# 27. AI Safety and Reliability Rules

## Rule 1 — No fabrication

Never invent:

- Jobs
- Companies
- Skills
- Technologies
- Achievements
- Degrees
- Certifications
- Metrics
- Responsibilities

## Rule 2 — Evidence first

A generated claim should map to candidate evidence.

## Rule 3 — Ask when uncertain

Unknown information should trigger clarification instead of invention.

## Rule 4 — Preserve user control

AI-generated information must be editable.

## Rule 5 — Explain important changes

When the AI modifies a CV, the user should be able to inspect relevant changes.

---

# 28. Database Entities

Initial entities:

```text
User
CandidateProfile
Skill
CandidateSkill
Experience
Education
Certification
Achievement
Project
ProjectTechnology
Evidence
GitHubAccount
GitHubRepository
Job
JobRequirement
RequirementMatch
ClarificationQuestion
ClarificationAnswer
Application
ApplicationStatusHistory
Document
CVVersion
CoverLetterVersion
InterviewPreparation
InterviewQuestion
```

Relationships should be normalized where practical.

---

# 29. API Requirements

## Authentication

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
```

## Profile

```http
GET    /api/profile
PUT    /api/profile
GET    /api/profile/skills
POST   /api/profile/skills
GET    /api/profile/projects
POST   /api/profile/projects
PUT    /api/profile/projects/:id
DELETE /api/profile/projects/:id
```

## Documents

```http
POST /api/documents/upload
GET  /api/documents
GET  /api/documents/:id
DELETE /api/documents/:id
```

## GitHub

```http
GET  /api/github/connect
GET  /api/github/callback
GET  /api/github/repositories
POST /api/github/repositories/:id/analyze
```

## Jobs

```http
POST /api/jobs
POST /api/jobs/analyze
GET  /api/jobs
GET  /api/jobs/:id
```

## Matching

```http
POST /api/jobs/:id/match
GET  /api/jobs/:id/matches
GET  /api/jobs/:id/questions
POST /api/jobs/:id/questions/:questionId/answer
```

## CV

```http
POST /api/jobs/:id/cv/generate
GET  /api/cv/:id
POST /api/cv/:id/regenerate
GET  /api/cv/:id/export/pdf
GET  /api/cv/:id/export/docx
```

## Cover Email

```http
POST /api/jobs/:id/cover-email/generate
```

## Interview

```http
POST /api/jobs/:id/interview/generate
GET  /api/jobs/:id/interview
```

## Applications

```http
POST  /api/applications
GET   /api/applications
GET   /api/applications/:id
PATCH /api/applications/:id
DELETE /api/applications/:id
```

---

# 30. Background Jobs

Long-running operations must use background workers.

Examples:

- CV parsing
- OCR
- GitHub repository analysis
- Embedding generation
- Bulk repository analysis
- PDF generation
- DOCX generation
- Interview generation

Architecture:

```text
FastAPI
   |
   v
Redis Queue
   |
   v
Worker
   |
   v
Database / Object Storage
```

---

# 31. File Storage

Store uploaded/generated files in object storage.

Do not store large binary files directly in PostgreSQL.

Database stores:

- File metadata
- Storage key
- MIME type
- Size
- Owner
- Created time
- Version

---

# 32. Security Requirements

- Encrypt secrets.
- Never expose Gemini API keys to the frontend.
- Validate uploaded file types.
- Limit upload size.
- Scan uploaded files where appropriate.
- Use signed object-storage URLs.
- Implement authorization on every resource.
- Users must only access their own data.
- Encrypt sensitive data at rest where appropriate.
- Avoid logging CV contents or API secrets.
- Implement rate limiting.
- Sanitize extracted document content before rendering.
- Protect OAuth tokens.
- Support account/data deletion.

---

# 33. Privacy Requirements

The application contains sensitive professional information.

Users must be able to:

- View stored information
- Edit information
- Delete information
- Delete uploaded files
- Delete account
- Export their profile/data

AI requests should send only information necessary for the current task.

---

# 34. Frontend Pages

## Public

```text
/
 /pricing
 /login
 /register
 /privacy
 /terms
```

## Authenticated

```text
/dashboard

/profile
/profile/personal
/profile/experience
/profile/education
/profile/skills
/profile/projects
/profile/documents

/jobs
/jobs/new
/jobs/:id
/jobs/:id/analyze
/jobs/:id/cv
/jobs/:id/interview

/applications
/applications/:id

/settings
```

---

# 35. Dashboard

Dashboard should show:

- Total applications
- Active applications
- Interviews
- Offers
- Recent applications
- Recent generated CVs
- Profile completeness
- Pending clarification questions

---

# 36. Profile Completeness

Calculate profile completeness from required data.

Example:

```text
Profile completeness: 82%

Personal information     ✓
Experience               ✓
Education                ✓
Skills                   ✓
Projects                 ✓
GitHub                   ✓
Achievements             !
LinkedIn                 !
```

---

# 37. Error Handling

API errors should use a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "JOB_ANALYSIS_FAILED",
    "message": "Unable to analyze the job description."
  }
}
```

Never expose internal stack traces to clients.

---

# 38. Observability

Implement:

- Structured logging
- Request IDs
- Error tracking
- AI request metadata
- AI latency
- Token usage where available
- Cost tracking
- Background-job status

Do not log private document contents unnecessarily.

---

# 39. Testing

## Backend

- Unit tests
- Integration tests
- API tests
- AI schema validation tests
- Authorization tests

## Frontend

- Component tests
- Form validation tests
- End-to-end tests

## AI

Create a fixed evaluation dataset containing:

- Job descriptions
- Candidate profiles
- Expected extracted requirements
- Expected evidence mappings
- Hallucination cases

AI output must be evaluated before production releases.

---

# 40. MVP Development Phases

## Phase 1 — Foundation

- Repository setup
- Docker
- PostgreSQL
- Redis
- FastAPI
- Next.js
- Authentication
- Database migrations
- Base UI

## Phase 2 — Candidate Profile

- Onboarding
- CV upload
- CV parsing
- Profile extraction
- Profile editor
- Candidate Knowledge Base

## Phase 3 — GitHub

- GitHub OAuth
- Repository listing
- Repository analysis
- Project extraction
- Evidence mapping

## Phase 4 — Job Intelligence

- Job input
- Job parser
- Job analysis
- Requirement extraction
- Candidate/job matching
- Clarification engine

## Phase 5 — Documents

- CV generation
- Templates
- ATS analysis
- PDF export
- Cover email
- Cover letter

## Phase 6 — Applications

- Application tracker
- Status history
- Document versions
- Notes

## Phase 7 — Interview

- Technical questions
- Project questions
- Behavioral questions
- Interview preparation

## Phase 8 — Production Hardening

- Security
- Rate limiting
- Monitoring
- AI evaluation
- Performance
- Backup
- Deployment

---

# 41. Definition of Done for MVP

The MVP is complete when a new user can:

```text
Register
   ↓
Upload old CV
   ↓
Review extracted profile
   ↓
Connect GitHub
   ↓
Analyze projects
   ↓
Paste a job description
   ↓
Analyze job
   ↓
Review requirement matching
   ↓
Answer missing-information questions
   ↓
Generate tailored CV
   ↓
Generate application email
   ↓
Generate interview questions
   ↓
Create application record
   ↓
Track application status
```

All generated content must be editable and traceable to candidate information.

---

# 42. Product Principles

1. Truth over optimization.
2. Evidence over assumptions.
3. User control over automation.
4. Structured data over unstructured prompts.
5. Reusable candidate profile over repeated CV parsing.
6. Explainability over opaque AI output.
7. Modular AI provider architecture.
8. Privacy by design.
9. ATS compatibility without keyword stuffing.
10. Human review before application submission.
