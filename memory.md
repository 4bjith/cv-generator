# AI CV Maker — Development Memory

**Last updated:** 2026-10-20  
**Project status:** Phase 9 complete; Personal Autonomous AI Job Acquisition Agent fully implemented with multi-source fresher-friendly discovery, Playwright browser automation, QA Memory Bank, Recruiter Outreach multiplier, daily APScheduler (07:00 AM IST), and comprehensive Next.js command dashboard; 115 backend and 99 frontend tests passing with 0 TypeScript errors.

## Purpose

AI CV Maker is an AI-powered job application assistant and personal autonomous job acquisition agent. It maintains a structured, evidence-backed professional profile for candidate Abhijith AT, discovers opportunities across official career pages and public ATS feeds, matches job requirements with verified candidate evidence without fabrication, answers application forms deterministically or with supervision, executes Playwright browser submissions, generates tailored CV snapshots and cover letters, drafts recruiter visibility outreach, tracks applications, and delivers morning briefing reports.

The product is not only a resume generator. Its differentiator is the intersection of:

```text
Candidate Knowledge Base
        +
Autonomous Job Discovery & Fresher Evaluation
        +
Evidence-based Matching & Document Tailoring
        +
Playwright Application Execution & QA Memory
        +
Recruiter Visibility & Application Tracking
```

Generated content must be truthful, ATS-friendly, editable, versioned, and traceable to candidate evidence.

## Source documentation

- [`FRD.md`](./FRD.md) — complete product requirements and MVP definition.
- [`CODING_AGENT_CONTEXT.md`](./CODING_AGENT_CONTEXT.md) — architecture, implementation rules, security principles, and agent behavior.
- [`autonomous_job_application_system_architecture.md`](file:///C:/Users/abhij/.gemini/antigravity-ide/brain/945ae54e-999b-421d-a521-2d0145e94c12/autonomous_job_application_system_architecture.md) — full architectural blueprint for the autonomous agent.
- [`personal_job_acquisition_agent_audit_and_plan.md`](file:///C:/Users/abhij/.gemini/antigravity-ide/brain/945ae54e-999b-421d-a521-2d0145e94c12/personal_job_acquisition_agent_audit_and_plan.md) — audit findings, design decisions, and implementation plan.

## Non-negotiable product rules

1. Never fabricate experience, skills, technologies, projects, education, achievements, metrics, or responsibilities.
2. Treat the database-backed Candidate Knowledge Base as the source of truth; the LLM is an intelligence layer, not the database.
3. Use evidence states (`OBSERVED`, `USER_CONFIRMED`, `INFERRED`, `UNKNOWN`) and do not turn weak or unknown evidence into factual claims.
4. Ask the user when information is missing or ambiguous.
5. Keep AI-generated content editable and do not silently modify permanent profile data.
6. Keep Gemini behind an internal provider abstraction with configurable model names.
7. External applications must default to Supervised Mode (pre-fills form, captures screenshot, awaits 1-click submit) with optional Autonomous Submit toggle and a Global Emergency Stop.

## Target architecture

- Frontend: Next.js, TypeScript, App Router, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form, Zod.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Pytest, Playwright, APScheduler.
- Data and infrastructure: PostgreSQL + pgvector, Redis, S3-compatible storage, Docker.
- AI: Google Gemini through an internal `AIProvider` interface for text, structured output, vision, embeddings, and token counting.
- Backend layering: API → service → repository → database. AI belongs in services, not route handlers.

## Feature map

| Area | Status | Notes |
| --- | --- | --- |
| Repository scaffolding | Complete | Next.js frontend and layered FastAPI backend are available and validated. |
| Frontend foundation | Complete | Next.js 16.3.8 App Router with TypeScript, Tailwind CSS, ESLint, and npm. |
| Backend foundation | Complete | FastAPI 0.142.2 with versioned `/api/v1/health`, structured JSON logging, correlation IDs, centralized exception handling, security middlewares, Dockerfile, and pytest suite. |
| Authentication foundation | Complete | JWT access/refresh token pairs, bcrypt hashing, stateless API routes (`/api/v1/auth/{register,login,me,refresh,logout}`), `get_current_user` dependency, and repository pattern abstraction. |
| Candidate profile / Knowledge Base | Complete | Master career knowledge base domain model, PostgreSQL schema with Alembic migration, normalized child entities, structured metrics, ProfileService, readiness scoring, TanStack Query integration, and full-stack responsive UI. Pre-seeded with Abhijith AT's verified profile data. |
| CV import and parsing | Not started | PDF, DOCX, TXT, and image inputs; preserve original files; require review before persistence. |
| GitHub & Portfolio integration | Complete | Verified links extracted (GitHub: `https://github.com/4bjith/`, Portfolio: `https://4bjith.github.io/Portfolio-Website/`, LinkedIn: `https://www.linkedin.com/in/abhijith-4bjith/`). |
| Job input and analysis | Complete | Saved job targets with full CRUD, employment type capture, modular extraction pipeline (mandatory vs preferred, seniority, categories, keywords), and validation. |
| Autonomous Job Discovery | Complete | Multi-source adapters (Direct ATS Greenhouse/Lever boards, Jobicy remote feeds, Kerala tech hubs Kozhikode/Kochi/Kannur). Deduplication by title/company/URL hash. |
| Intelligent Fresher Evaluation | Complete | Fresher-friendly scoring engine: evaluates skills (React, Node, Express, MongoDB, JavaScript), recognizes equivalent project experience, handles Kerala & Remote locations, outputs explainable score & rationale. |
| Requirement matching | Complete | Canonical `JobRequirementItem`, evidence-grounded matching against candidate knowledge base, strict non-hallucination, full evidence traceability, gap distinction, and non-mutating CV version snapshot creation. |
| Clarification engine & AI tailoring | Complete | Resumable sessions, prioritized questions, evidence provenance tracking (`candidate_clarification`, `unverified`), profile promotion, zero-hallucination tailoring, independent `CVVersion` snapshot creation, template switching, PDF/DOCX export compatibility, and full-stack UI. |
| CV generation and ATS analysis | Complete | AI CV tailoring, 6 template renderers, PDF/DOCX exporters, explainable ATS scoring (0-100), keyword density auditing, and evidence-grounded keyword optimization complete. |
| Cover email / cover letter | Complete | Grounded in CandidateProfile & confirmed clarifications; configurable tone, length, instructions; independent draft editing, duplication, version-preserving regeneration; multi-format PDF/DOCX exports. |
| Autonomous Application Engine | Complete | Playwright browser automation (`playwright_runner.py`), headless form navigation, heuristic field mapping (name, email, phone, links, resume upload), QA Memory Bank resolution, screenshot capture, confirmation detection, and dual Supervised/Autonomous submission modes. |
| QA Memory Bank | Complete | Persistent repository of candidate answers for recurring application questions (work authorization, notice period, relocation, salary expectations). Auto-learns from user answers. |
| Recruiter Outreach & Visibility | Complete | AI recruiter intelligence: generates 300-char LinkedIn connect notes, concise cold emails, referral requests, and schedules Day 4 & Day 9 response-aware follow-ups. |
| Application Tracker & Follow-Ups | Complete | Unified pipeline tracking statuses (`discovered`, `shortlisted`, `tailored`, `prefilled`, `submitted`, `confirmed`, `interview`, `rejected`), submission evidence, screenshots, and follow-up reminders. |
| Daily Agent Scheduler & Morning Report | Complete | APScheduler running daily at 07:00 AM IST. Discovers jobs, evaluates, tailors documents, prepares applications, drafts outreach, and generates comprehensive morning briefing reports. |
| Agent Command Dashboard | Complete | Dedicated Next.js command center with tabs for Morning Briefing, Discovered Jobs, Applications Pipeline, Recruiter Outreach Studio, QA Memory Bank, and Preferences. Includes Emergency Stop & Run Agent Now controls. |
| Testing and production hardening | Complete | 115/115 backend pytest tests passing, 99/99 frontend vitest tests passing, 0 TypeScript errors, Next.js production build verified. |

## Recommended implementation order

1. Project scaffolding, Docker, PostgreSQL, Redis, and environment configuration.
2. Authentication and authorization.
3. Candidate profile database models, migrations, schemas, repositories, services, and APIs.
4. CV upload, file validation, parsing, structured extraction, and profile review UI.
5. Gemini provider abstraction, structured output validation, retries, and failure states.
6. GitHub OAuth and selective repository/project analysis.
7. Job input, extraction, job analysis, requirement matching, and clarification.
8. CV generation, templates, rendering, ATS analysis, cover email, and cover letter.
9. Application tracker, immutable document versions, interview preparation, and audit metadata.
10. Testing, AI evaluation cases, security, observability, cost controls, performance, and deployment.

## Dependency policy

For new packages, prefer the latest stable release that is compatible with the current runtime and framework. Verify the version from the official package registry or documentation, avoid canary releases unless explicitly requested, and record important version choices here. Keep lockfiles and package metadata committed when the repository is initialized for version control.

## Feature-change permission policy

The user has requested explicit permission before changing any existing feature or its behavior. Future work must:

- inspect the existing implementation first;
- explain the proposed change, affected files, and behavior impact;
- ask for permission before modifying an existing feature;
- proceed without additional permission only for new features, requested documentation maintenance, bug fixes the user explicitly asked for, or necessary implementation steps within an already approved task;
- never silently remove or alter existing functionality.

## Memory maintenance rule

Whenever a feature is completed, the LLM must update this file in the same task. Each update should record:

- feature name and status;
- user-visible behavior;
- backend, frontend, schema, migration, prompt, or configuration files changed;
- validation/tests run and their results;
- evidence/safety considerations for AI features;
- known limitations and next steps;
- date of the update.

If a feature is only partially complete, keep it marked `In progress` and list the exact remaining work. Do not mark a feature complete because only its UI or a happy path works.

## Current workspace baseline

- Product requirements and coding-agent guidance are present.
- Frontend and backend foundation scaffolds are present; database migrations, authentication, and product features remain to be built.
- No existing product feature was changed; this task created the initial implementation foundation.
- The workspace is not currently initialized as a Git repository at the inspected path.
- `create-next-app` initialized a nested Git repository inside `frontend/`; the project root remains the intended workspace root.
- Root-local agent skills added under `.agents/skills/`: `frontend-design` for product-specific visual direction and `web-design-guidelines` for accessibility, interaction, performance, and UI review guidance.

## Development log

### 2026-10-02 — Documentation baseline

- Read and summarized `FRD.md` and `CODING_AGENT_CONTEXT.md`.
- Created this `memory.md` file.
- Added the completed-feature memory update rule and explicit permission rule to `CODING_AGENT_CONTEXT.md`.
- Added root-local UI/frontend skills from Anthropic and Vercel agent-skill repositories.
- No product feature behavior was changed; this was new foundation work.
- Validation: backend `pytest` passed; frontend `npm run lint` passed; frontend `npm run build` passed.

### 2026-10-02 — Frontend and backend foundation

- Created `frontend/` with Next.js 16.3.8, React 19.2.8, TypeScript, Tailwind CSS 4.3.3, ESLint, App Router, and npm lockfile.
- Created `backend/` with FastAPI 0.142.2, Pydantic 2.13.5, Uvicorn 0.54.0, `pydantic-settings`, pytest, and pytest-asyncio.
- Added layered backend package directories and a working `/api/health` endpoint.
- Added backend packaging via `backend/pyproject.toml`, local `.venv`, CORS for `http://localhost:3000`, and a health endpoint test.
- Replaced the generated Google-hosted Geist font import with a local system font stack so production builds do not require external font access.
- Added root `.gitignore` for frontend and backend generated artifacts.
- Validation results: 1 backend test passed; frontend lint passed; frontend production build passed with Next.js 16.3.8 and Turbopack.
- Remaining work: database/infrastructure setup, authentication, profile domain, and all MVP features in the priority order above.

### 2026-10-05 — Backend infrastructure & authentication foundation

- Implemented versioned `/api/v1` routing with `/api/v1/health/live`, `/api/v1/health/ready`, and backward-compatible `/api/health`.
- Implemented structured machine-readable JSON logging (`app.core.logging`) with request IDs, response durations, and contextual trace data.
- Implemented request correlation ID tracking middleware (`X-Request-ID`) and security headers middleware (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, etc.).
- Created centralized exception handling mapping all errors to a standard `{ "error": { "code", "message", "request_id", "details" } }` contract.
- Built JWT authentication system with access/refresh token pairs, bcrypt password hashing, `get_current_user` FastAPI dependency, and stateless user repository abstraction.
- Added endpoints: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`.
- Added multi-stage production `Dockerfile` and comprehensive `.env.example`.
### 2026-10-05 — Phase 1: Candidate Profile & Career Data Foundation

- **Domain Models & Database Architecture**:
  - Implemented normalized SQLAlchemy 2.x async models for candidate profile (`CandidateProfileModel`) and 10 nested child entities: `CandidateLinkModel`, `WorkExperienceModel`, `EducationModel`, `CandidateSkillModel`, `ProjectModel`, `CertificationModel`, `AchievementModel`, `LanguageModel`, and `CareerPreferencesModel`.
  - Added Alembic migration `0002_candidate_profile_and_career_data.py` with foreign keys (`ondelete="CASCADE"`), unique constraints, and PostgreSQL JSONB / SQLite JSON compatibility for structured arrays (`responsibilities`, `achievements`, `technologies`, `metrics`).
- **Pydantic Schemas & Validation**:
  - Full request/response schemas with date range validation (end date >= start date), URL validators, enums (`CareerLevel`, `EmploymentType`, `SkillCategory`, `SkillProficiency`, `LanguageProficiency`, `RemotePreference`, `AvailabilityStatus`, `AchievementCategory`, `LinkType`), and structured `ExperienceMetric` objects.
- **Repository & Service Layer**:
  - Created `IProfileRepository` and PostgreSQL async implementation with eager `selectinload` loading, scoped user queries, and duplicate skill prevention.
  - Built `ProfileService` containing business logic, ownership enforcement, and a deterministic 12-section profile readiness / strength scorecard calculation (0-100%).
- **REST Endpoints (`/api/v1/profile`)**:
  - Root profile CRUD (`GET`, `POST`, `PATCH`, `DELETE`) + `/profile/strength`.
  - Granular child resource endpoints: `/links`, `/experience`, `/education`, `/skills`, `/projects`, `/certifications`, `/achievements`, `/languages`, `/preferences`.
- **Frontend Master Career Knowledge Base UI**:
  - Built typed API client (`frontend/services/profile/profile.api.ts`) and TanStack Query hooks (`frontend/hooks/use-profile.ts`) with cache invalidation on mutations.
  - Implemented mobile-first modular section editors: `PersonalInfoSection`, `ProfessionalIdentitySection`, `ExperienceSection` (with responsibilities, achievements, and metric builder), `SkillsSection` (with categories & proficiency), `ProjectsSection` (with problem/solution & architecture), `EducationSection`, `CertificationsSection`, `AchievementsSection`, `LanguagesSection`, `PreferencesSection`, `ProfileStrengthPanel`, `InitialProfileCard`, and `ProfileEditor`.
  - Replaced prototype mock data in `ProfileView` and `page.tsx` with live TanStack Query profile state.
- **Automated Tests & Quality Verification**:
  - Backend: 30/30 tests passing (`pytest`) including `test_profile.py` suites covering CRUD, metric validation, duplicate handling, date ordering, and cross-user isolation.
  - Frontend: 26/26 tests passing (`vitest`) across 7 test suites including `profile-api.test.ts` and `use-profile.test.ts`.

### 2026-10-10 — Phase 2.1: Job Target Management

- **Domain Models & Database Architecture**:
  - Implemented SQLAlchemy 2.x async model `JobTarget` (`app/models/job_target.py`) with fields for `title`, `company_name`, `location`, `job_description`, `source_url`, `user_notes`, `status` (`saved`, `archived`), timestamps, and `user_id` foreign key with `ondelete="CASCADE"`.
  - Added Alembic migration `0004_job_targets.py` creating the `job_targets` table with indices on `user_id`, `status`, and `created_at`.
  - Verified and upgraded PostgreSQL database to revision `0004_job_targets`.
- **Pydantic Schemas & Validation**:
  - Implemented request/response schemas in `app/schemas/job_target.py`: `JobTargetCreate`, `JobTargetUpdate`, `JobTargetResponse`, `JobTargetListResponse`, and `JobTargetStatus` enum.
  - Added strict string stripping, required field validation, URL format checking (`http://` or `https://`), and max length bounds.
- **Repository & Service Layer**:
  - Created `IJobTargetRepository` interface and `PostgresJobTargetRepository` with pagination, case-insensitive search (matching title, company, or location), status filtering, and created_at sorting.
  - Built `JobTargetService` implementing complete business logic, user ownership isolation, and standard `404 Not Found` error handling for cross-user/missing access.
- **REST Endpoints (`/api/v1/jobs`)**:
  - `GET /api/v1/jobs`: List user's job targets with pagination, status filter, and search.
  - `POST /api/v1/jobs`: Create a new job target.
  - `GET /api/v1/jobs/{job_id}`: Retrieve single job target with strict ownership check.
  - `PATCH /api/v1/jobs/{job_id}`: Update permitted fields and status.
  - `DELETE /api/v1/jobs/{job_id}`: Delete a job target safely.
- **Frontend Workspace Integration**:
  - Created TypeScript definitions in `types/job.ts`.
  - Implemented typed API service client in `services/jobs/jobs.api.ts` and TanStack Query hooks in `hooks/use-jobs.ts` (`useJobList`, `useJobDetail`, `useCreateJob`, `useUpdateJob`, `useDeleteJob`).
  - Added centralized query keys `jobKeys` in `lib/query-keys.ts`.
  - Built responsive UI components in `components/jobs/`: `JobTargetsView`, `JobTargetModal` (for create and edit), `JobDetailModal`, and delete confirmation dialogs.
  - Wired live `JobTargetsView` into `app-shell.tsx` navigation ("Target Jobs") and `app/page.tsx` view routing.
- **Automated Tests & Quality Verification**:
### 2026-10-10 — Phase 2.2: CV Version Lifecycle and Snapshots

- **Domain Models & Database Architecture**:
  - Implemented `CVVersion` model (`app/models/cv_version.py`) with `id` (UUID primary key), `user_id` (`users.id` foreign key with `ondelete="CASCADE"`), `job_target_id` (`job_targets.id` foreign key with `ondelete="SET NULL"` for safe target detachment), `name` (String 200), `status` (String 50, default `"draft"`), `content_snapshot` (PostgreSQL `JSONB` / SQLite `JSON`), and timestamps.
  - Added Alembic migration `0005_cv_versions.py` with indexes on `user_id`, `job_target_id`, `status`, and `created_at`.
  - Upgraded PostgreSQL to revision `0005_cv_versions`.
- **Pydantic Schemas & Snapshot Validation Engine**:
  - Implemented comprehensive snapshot models in `app/schemas/cv.py`: `CVBasicsSnapshot`, `CVLinkSnapshot`, `CVExperienceSnapshot`, `CVEducationSnapshot`, `CVSkillSnapshot`, `CVProjectSnapshot`, `CVCertificationSnapshot`, `CVAchievementSnapshot`, `CVLanguageSnapshot`, `CVCareerPreferencesSnapshot`, `CVEvidenceItemSnapshot`, and root `CVContentSnapshot`.
  - Added request/response models: `CVVersionCreate`, `CVVersionUpdate`, `CVVersionDuplicate`, `CVVersionSummaryResponse`, `CVVersionResponse`, `CVVersionListResponse`, and `CVVersionStatus` enum (`draft`, `ready`, `archived`).
- **Repository & Service Layer**:
  - Created `ICVVersionRepository` interface and `PostgresCVVersionRepository` with pagination, case-insensitive search, status/job target filtering, and eager loading of `job_target` relationships.
  - Built `CVService` implementing:
    - Point-in-time profile serialization: copies full CandidateProfile structure and evidence association mappings into an isolated `CVContentSnapshot`.
    - Lifecycle actions: `create_version_from_profile`, `get_version`, `list_versions`, `update_version`, `duplicate_version` (deep-cloned independent snapshot), `archive_version`, `restore_version`, `delete_version`.
    - Cross-user ownership enforcement (standard 404 responses for unauthorized access attempts).
    - Validation ensuring linked `job_target_id` belongs to the authenticated user.
- **REST Endpoints (`/api/v1/cv/versions`)**:
  - `GET /api/v1/cv/versions`: List user's versions with search, status, and job target filters.
  - `POST /api/v1/cv/versions`: Create new independent CV version snapshot from CandidateProfile.
  - `GET /api/v1/cv/versions/{id}`: Retrieve single CV version with full point-in-time content snapshot.
  - `PATCH /api/v1/cv/versions/{id}`: Update metadata and/or version-specific content snapshot.
  - `POST /api/v1/cv/versions/{id}/duplicate`: Clone version with new ID and independent snapshot.
  - `POST /api/v1/cv/versions/{id}/archive`: Transition status to `archived`.
  - `POST /api/v1/cv/versions/{id}/restore`: Transition status to `draft`.
  - `DELETE /api/v1/cv/versions/{id}`: Delete CV version.
- **Frontend Integration**:
  - Created TypeScript definitions in `types/cv.ts`.
  - Built API client in `services/cv/cv.api.ts` and TanStack Query hooks in `hooks/use-cv.ts` (`useCvList`, `useCvDetail`, `useCreateCvVersion`, `useUpdateCvVersion`, `useDuplicateCvVersion`, `useArchiveCvVersion`, `useRestoreCvVersion`, `useDeleteCvVersion`).
  - Added `cvKeys` in `lib/query-keys.ts`.
  - Built responsive UI components in `components/cv/`: `CVVersionsView`, `CVVersionModal`, and `CVSnapshotModal`.
  - Integrated into `app/page.tsx` view routing.
- **Automated Tests & Quality Verification**:
  - Backend: 56/56 tests passing (`pytest`) including all 12 tests in `test_cv_versions.py` (snapshot immutability on master profile edits, version updates not altering master profile, duplication independence, safe ON DELETE SET NULL on job deletion, cross-user isolation, archive/restore, and filtering).
  - Frontend: 48/48 tests passing (`vitest`) across 11 test suites including `cv-api.test.ts` and `use-cv.test.ts`.
  - Next.js Production Build: Succeeded in 7.5s static generation with 0 TypeScript/lint errors.

### 2026-10-17 — Phase 3.1: CV Template Design System and Print Layouts

- **Template Registry Architecture**:
  - Implemented extensible template registry (`frontend/components/cv/templates/registry.ts`) supporting alias mapping, dynamic third-party/custom template registration, and strict separation between CV content, presentation settings, template configuration, and metadata.
  - Reusable, resilient semantic section components (`frontend/components/cv/templates/shared/semantic-sections.tsx`) providing structured rendering for Personal Header, Professional Summary, Work Experience (with metrics & technologies), Education, Skills (categorized, tags, inline), Key Projects, Certifications, Honors & Awards, and Languages.
  - Robust visibility and ordering filtering (`frontend/components/cv/templates/shared/helpers.ts`) supporting `section_order`, `section_visibility`, and individual `item_visibility`. Empty/hidden sections are omitted cleanly without empty headings.
- **Six Production-Grade CV Templates**:
  - **Modern Professional** (`modern-professional` / alias `modern`): Clean contemporary single-column layout, strong typographic hierarchy, sapphire accenting, compact spacing.
  - **Classic Executive** (`classic-executive` / alias `executive`): Formal serif typography (Georgia/serif), centered executive header with double rules, leadership progression focus.
  - **ATS-Friendly Minimal** (`ats-minimal` / alias `minimal`): Single-column text-first structure, standard headings, high contrast monochrome, zero parsing friction for applicant tracking systems.
  - **Technical / Software Developer** (`technical-developer` / alias `technical`): Categorized technical skills matrix, monospace tags, system project highlights, quantifiable metrics, GitHub/live links.
  - **Contemporary Two-Column** (`contemporary-two-column` / alias `two-column`): Asymmetric 32% sidebar (contact, skills, education, languages) + 68% main column (summary, experience, projects).
  - **Academic / Research** (`academic-research` / alias `academic`): Scholarly dense layout with academic serif styling, education-first hierarchy, publications, research experience, and grants.
- **Template Selection Experience & Print Layout**:
  - Responsive **Template Gallery** (`frontend/components/cv/templates/gallery/template-gallery.tsx`) with accurate CSS vector miniature previews, category badges, descriptions, and active state indicators.
  - Print & screen layout infrastructure (`frontend/components/cv/templates/layout/cv-print-layout.tsx` & `frontend/styles/cv-templates.css`) supporting A4 (210mm x 297mm) and US Letter (8.5in x 11in), spacing density modes (compact, normal, relaxed), zoom preview, and `@media print` rules for clean page breaks without overflow or clipping.
  - Integrated into `CVVersionEditor` with "Edit Content" vs "Preview & Templates" mode switcher, and `CVSnapshotModal` with formatted preview and print options.
- **Backend Schema & Persistence**:
  - Extended `CVPresentationSnapshot` in `backend/app/schemas/cv.py` and `frontend/types/cv.ts` with optional `page_size` and `spacing` fields, maintaining 100% backward compatibility and seamless JSON persistence.
- **Automated Tests & Quality Verification**:
  - Backend: 61/61 tests passing (`pytest`) including all `test_cv_versions.py` and persistence suites.
  - Frontend: 66/66 tests passing (`vitest`) across 13 test suites including comprehensive `cv-templates.test.ts`.
  - Next.js Production Build: Successfully compiled in 2.7s with 0 TypeScript/lint errors and static page generation.
  - End-to-End Browser Subagent: Full browser recording verified (`cv_templates_preview_1792211289389.webp`).

### 2026-10-17 — Phase 3.2: Production-Quality PDF and DOCX Export

- **PDF Export Engine (`backend/app/services/export/pdf_exporter.py`)**:
  - Implemented high-resolution, vector-based PDF generation using ReportLab Platypus (`BaseDocTemplate`, `PageTemplate`, `Frame`, `Paragraph`, `Table`, `HRFlowable`).
  - Text is 100% searchable and selectable (zero rasterized screenshots/images of text).
  - Exact support for both `A4` (595.27 x 841.89 pt) and `US Letter` (612 x 792 pt) page dimensions.
  - Full support for configurable spacing densities: `compact` (36 pt margin), `normal` (48 pt margin), and `relaxed` (60 pt margin).
  - Modular styling supporting all 6 templates:
    - `modern-professional`: Accent bars, clean typography, right-aligned dates, skill tags.
    - `classic-executive`: Dignified centered header, serif typography, leadership progression.
    - `ats-minimal`: 100% linear, high contrast monochrome, standard headings and bullets.
    - `technical-developer`: Monospace accents, categorized technical matrix, system tech stacks.
    - `contemporary-two-column`: Multi-frame layout with 33% sidebar + 67% main column and seamless `NextPageTemplate` multi-page overflow.
    - `academic-research`: Scholarly serif layout, education-first hierarchy, publications, research experience, and awards.
  - Multi-page two-pass `NumberedCanvas` displaying clean right-aligned page numbering ("Page X of Y") for multi-page documents.
- **DOCX Export Engine (`backend/app/services/export/docx_exporter.py`)**:
  - Implemented native, editable Microsoft Word (`.docx`) document generation using `python-docx`.
  - Genuine Word document structures: headings (`Heading 1`, `Heading 2`, `Heading 3`), body paragraphs, `List Bullet` styles, OpenXML hyperlinking (`<w:hyperlink>`), and borderless alignment tables for roles, companies, and dates.
  - Section page sizes (`A4` = 8.27 x 11.69 in, `US Letter` = 8.5 x 11 in) and configurable margins.
  - Word-native typography mappings: Arial (`sans`), Times New Roman (`serif`), Courier New (`mono`).
  - Word paragraph border lines under headings and table cell background shading for the two-column sidebar.
  - Opens cleanly without repair warnings in Microsoft Word, LibreOffice Writer, and Google Docs.
- **API Endpoints & Security (`backend/app/api/routes/cv.py`)**:
  - `GET /api/v1/cv/versions/{version_id}/export/pdf`: Authenticated, owner-isolated PDF export with query parameter overrides.
  - `GET /api/v1/cv/versions/{version_id}/export/docx`: Authenticated, owner-isolated DOCX export with query parameter overrides.
  - Proper MIME types: `application/pdf` and `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.
  - Sanitized filenames via `Content-Disposition: attachment; filename="{Candidate_Name}_CV.pdf"`.
- **Frontend Integration (`frontend`)**:
  - Extended API client (`frontend/services/cv/cv.api.ts`) with `exportPdf` and `exportDocx` blob handlers.
  - Added TanStack Query mutation hooks (`frontend/hooks/use-cv.ts`): `useExportPdf` and `useExportDocx` with automated browser download triggers.
  - Updated `CVVersionEditor` (`frontend/components/cv/cv-version-editor.tsx`) with clearly styled "Export PDF" and "Export DOCX" action buttons.
  - Updated `CVPrintLayout` (`frontend/components/cv/templates/layout/cv-print-layout.tsx`) with dedicated "Download PDF" and "Download Word (.docx)" action buttons in the print layout toolbar.
  - Complete loading states, error toasts, and prevention of duplicate export requests.
- **Automated Tests & Quality Verification**:
  - Backend: 71/71 tests passing (`pytest`) including 10 comprehensive tests in `test_cv_export.py` testing all 6 templates, page dimensions, multi-page flows, text extraction via `pypdf`, DOCX zip structure verification, cross-user isolation, and malformed snapshot resilience.
  - Frontend: 69/69 tests passing (`vitest`) across 13 test suites.
  - Next.js Production Build: Compiled in 14.2s with static page generation and zero TypeScript errors.
  - End-to-End Browser Subagent: Visual verification recorded in `cv_export_actions_verified_1792214513657.webp` and screenshot `cv_export_preview_1792214614321.png`.

### 2026-10-17 — Phase 4: Job Description Intelligence Foundation & Evidence-Grounded Matching

- **Database & Persistence Layer**:
  - Alembic migration `backend/alembic/versions/0006_job_target_analysis_and_employment_type.py` cleanly applied to PostgreSQL.
  - Extended `JobTarget` model with `employment_type` (`String(50)`) and `analysis_result` (`JSONB` / SQLite-compatible `JSON_TYPE`).
  - Added strict ownership isolation and validation: title (1-200 chars), company (1-200 chars), description (10-50,000 chars), valid HTTP/HTTPS URLs, and status transitions.
- **Canonical Requirement & Analysis Schemas (`backend/app/schemas/job_target.py` & `frontend/types/job.ts`)**:
  - `JobRequirementItem`: canonical model `{ id, category, requirement, is_mandatory, candidate_match_status }` with auxiliary fields `{ reasoning, matched_entity_type, matched_entity_id, matched_entity_name, evidence_ids, evidence_items, confidence_score, gap_type }`.
  - `CandidateMatchStatus`: `"supported" | "partial" | "unverified" | "missing"`.
  - `GapType`: `"absent_from_profile" | "unverified_claim" | "skill_gap"`.
  - `EvidenceTraceItem`: `{ id, title, source, source_type, url, verification_status, date }`.
  - `KeywordSummary`: `{ total_requirements, mandatory_count, preferred_count, supported_count, partial_count, unverified_count, missing_count, coverage_percentage, mandatory_coverage_percentage, top_matched_keywords, top_missing_keywords, identified_gaps }`.
- **Modular Requirement Extraction Pipeline (`backend/app/services/job_intelligence/`)**:
  - `extractor_interface.py`: `IJobExtractor` abstract base class defining pluggable contract for heuristic NLP and AI providers (e.g. Gemini).
  - `extractor.py`: `RuleBasedJobExtractor` classifying seniority level, employment type, mandatory vs preferred requirements (detecting required, mandatory, must have, minimum, essential vs preferred, nice to have, plus, bonus), category categorization (`skills`, `technologies`, `experience`, `education`, `certifications`, `responsibilities`, `constraints`), and keyword extraction with resilient fallback handling for malformed or unstructured inputs.
- **Evidence-Grounded Candidate Matching Engine (`backend/app/services/job_intelligence/matcher.py`)**:
  - Zero hallucination guarantee: matches exclusively against confirmed records in candidate knowledge base (`CandidateProfile` skills, work experience accomplishments, projects, education, certifications, and links).
  - Polymorphic evidence indexing: indexes candidate `EvidenceItem` records by `entity_type:entity_id` and by ID, attaching verified `EvidenceTraceItem` references to matched requirements.
  - Gap distinction: accurately categorizes whether an unmet requirement is missing because it is completely absent from the profile (`absent_from_profile`), mentioned without verifiable artifact (`unverified_claim`), or falls short of depth/seniority thresholds (`skill_gap`).
  - Non-mutation guarantee: performing analysis strictly updates the `analysis_result` column on the targeted job, without ever mutating the master `CandidateProfile` or existing frozen `CVVersion` snapshots.
- **Job Intelligence Service & API Endpoints (`backend/app/api/routes/jobs.py`)**:
  - `POST /api/v1/jobs/{job_id}/analyze`: Runs extraction and candidate evidence matching, persists analysis result, returns complete analysis with explainability.
  - `GET /api/v1/jobs/{job_id}/analysis`: Retrieves cached analysis result, or triggers analysis if not yet run.
  - `POST /api/v1/jobs/extract`: Standalone modular requirement extraction for preview/validation.
  - `GET /api/v1/jobs/{job_id}/versions`: Retrieves all CV versions associated with the specific target job.
  - Strict ownership and cross-user isolation verified with 403 Forbidden checks.
- **Frontend User Experience (`frontend`)**:
  - `frontend/services/jobs/jobs.api.ts` & `frontend/hooks/use-jobs.ts`: Full TanStack Query hooks for job targets, analyses, extractions, and version associations.
  - `JobTargetModal` (`frontend/components/jobs/job-target-modal.tsx`): Full CRUD modal with `Employment Type` dropdown (Full-time, Contract, Part-time, Internship, Remote, Hybrid) and client validation.
  - `JobAnalysisModal` (`frontend/components/jobs/job-analysis-modal.tsx`): Clean, responsive modal displaying role overview, coverage progress indicators (Total Match %, Must-Haves %, Supported, Partial, Unverified, Missing counts), multi-dimensional filtering (All, Required, Preferred, status dropdown, category dropdown, search input), evidence cards with external links, unverified claim warnings, gap recommendations, and primary "Create Targeted CV" action.
  - `JobTargetsView` (`frontend/components/jobs/job-targets-view.tsx`): Enhanced job cards with match percentage badges, employment type chips, and direct "Analyze Match" trigger.
  - `CVVersionModal` (`frontend/components/cv/cv-version-modal.tsx`): Seamless workflow to create an immutable point-in-time CV version snapshot pre-linked to the target job opportunity.
- **Automated Tests & Quality Verification**:
  - Backend: **76/76 tests passing** (`pytest`) including `test_job_intelligence.py` verifying full CRUD with employment type, requirement extraction with mandatory/preferred discrimination, evidence-grounded matching with gap classification and non-hallucination, job-associated CV versions, and cross-user isolation.
  - Frontend: **77/77 tests passing** (`vitest`) across 14 test suites including `job-api.test.ts`, `use-jobs.test.ts`, and `job-analysis.test.ts`.
  - Type Safety: TypeScript compiler completed with **0 errors**.
  - Production Build: Next.js Turbopack build compiled successfully in 7.7s with **0 errors** and static page prerendering.
  - End-to-End Browser Subagent: Full browser recording verified (`job_intelligence_e2e_1792220638999.webp`, `job_intel_verification_1792220137619.webp`, `targeted_cv_creation`), capturing modal inspection, requirement filtering, and targeted CV snapshot creation.

### 2026-10-18 — Phase 5: Clarification Engine and Evidence-Grounded AI CV Tailoring

- **Database & Persistence Layer**:
  - Alembic migration `backend/alembic/versions/0007_clarification_data.py` cleanly applied to PostgreSQL (`alembic upgrade head`).
  - Added `clarification_data` (`JSONB` / SQLite-compatible `JSON_TYPE`) to `JobTarget` model (`backend/app/models/job_target.py`).
  - Safe transaction boundaries for session creation, answer persistence, and version snapshot generation.
- **AI Provider Subsystem (`backend/app/ai/`)**:
  - `interface.py`: Pluggable `AIProviderInterface` defining structured text generation, JSON schema validation, and vector embeddings.
  - `gemini_provider.py`: Google Gemini API client with exponential backoff retries and structured parsing.
  - `mock_provider.py`: Deterministic mock provider specialized for structured CV tailoring outputs and offline test environments.
  - `factory.py`: `get_ai_provider()` selecting live Gemini provider when API key is configured or deterministic mock provider for test/offline environments.
- **Clarification Subsystem (`backend/app/services/clarification_service.py`)**:
  - Prioritized question generation from job requirements analysis: mandatory gap questions generated at priority 1, preferred gap questions at priority 2.
  - Resumable, persistent clarification sessions stored in `JobTarget.clarification_data`.
  - Full support for single answer updates, skips, bulk answer submissions, and question-level profile promotion.
  - Provenance tracking: candidate-confirmed claims receive provenance tag `candidate_clarification` and verification status `unverified` (never automatically marked verified).
- **Evidence-Grounded CV Tailoring Engine (`backend/app/services/cv_tailoring_service.py`)**:
  - Zero-hallucination prompt assembly strictly grounding CV content in `CandidateProfile` evidence and confirmed clarifications.
  - Post-generation validation prevents unsupported claims: unconfirmed candidate requirements are captured in `unresolved_gaps` rather than fabricated.
  - Independent `CVVersion` creation: persists a standalone point-in-time `CVContentSnapshot` (v2.0.0 schema) without mutating the master `CandidateProfile` or altering prior CV version snapshots.
  - Full compatibility with the existing 6-template design system and PDF/DOCX export pipelines.
- **REST Endpoints (`backend/app/api/routes/jobs.py`)**:
  - `GET /api/v1/jobs/{job_id}/clarifications`: Retrieve or initialize persistent clarification session.
  - `POST /api/v1/jobs/{job_id}/clarifications/{question_id}/answer`: Submit candidate answer with optional profile persistence flag.
  - `POST /api/v1/jobs/{job_id}/clarifications/{question_id}/skip`: Mark question as skipped.
  - `POST /api/v1/jobs/{job_id}/clarifications/{question_id}/promote`: Promote confirmed answer to master candidate profile as unverified evidence.
  - `POST /api/v1/jobs/{job_id}/clarifications/bulk`: Bulk answer submission.
  - `POST /api/v1/jobs/{job_id}/tailor-cv`: Evidence-grounded CV generation returning tailored `CVVersion` snapshot with change summaries and unresolved gap warnings.
  - `POST /api/v1/jobs/{job_id}/cv/generate`: Canonical alias matching FRD spec.
- **Frontend Architecture & Components (`frontend`)**:
  - Types & Services: `types/clarification.ts`, `types/tailoring.ts`, `services/jobs/jobs.api.ts`, and TanStack Query hooks in `hooks/use-jobs.ts`.
  - `ClarificationModal` (`components/clarification/clarification-modal.tsx`): Interactive prioritized question flow with inline answer input, skip action, profile promotion consent, and primary "Generate Tailored CV" button.
  - `TailoringResultModal` (`components/clarification/tailoring-result-modal.tsx`): Verification banner (100% evidence grounded), change summary list, unresolved gap warnings, live 6-template switcher, and direct PDF/DOCX downloads.
  - `ClarificationsView` (`components/clarification/clarifications-view.tsx`): Full-screen clarification management with job switcher, session resumption, and CV generation.
  - Wired into `JobTargetsView` ("Clarify & Tailor" button on each card), `JobAnalysisModal` ("Clarify & Tailor" action), and `app/page.tsx` view routing.
- **Automated Tests & Quality Verification**:
  - Backend: **81/81 tests passing** (`pytest`) including `test_clarification_and_tailoring.py` covering prioritization, session resumption, unverified claim provenance, non-mutation of profile and versions, zero-hallucination filtering, and PDF/DOCX export integration.
  - Frontend: **83/83 tests passing** (`vitest`) across 15 test suites including `clarification-and-tailoring.test.ts`.
  - Type Safety: TypeScript compiler completed with **0 errors** (`npx tsc --noEmit`).
  - Production Build: Next.js Turbopack build compiled successfully in 15.2s with **0 errors** and static page prerendering.

### 2026-10-18 — Phase 6: ATS Analysis, Explainable Scoring & Keyword Optimization

- **Explainable Scoring Engine (`backend/app/services/ats_service.py`)**:
  - Deterministic 0-100 scoring model distinguishing between job-targeted mode and general baseline mode.
  - Job-Targeted Scoring Weights:
    - Keyword Coverage (30 points): Evaluates ratio of matched mandatory (double-weighted) and preferred job keywords.
    - Requirement Match (30 points): Assesses satisfaction of extracted job requirements with severe deductions for missing mandatory qualifications.
    - Structure & Completeness (20 points): Audits essential resume sections (basics, work experience, education, skills, contact phone/email) and reverse-chronological date consistency.
    - Format & Parsing Safety (20 points): Checks single-column layout friendliness, flags multi-column templates (such as `two-column`), scans for non-standard symbol/bullet friction, and identifies keyword stuffing.
  - General ATS Baseline Mode: Used when evaluating a CV without a target job. Reallocates weights to Skills Depth (30 pts), Structural Completeness (40 pts), and Format/Parsing Safety (30 pts).
  - Explicit heuristics notice: Mandatory legal disclaimer that scores are heuristic estimates and do not guarantee ATS parser passage or hiring decisions.
- **Parsing Friction & Keyword Stuffing Heuristics**:
  - Detects keyword stuffing when keyword density exceeds 3.5%, applying graduated penalty deductions to Format & Parsing Safety.
  - Assesses template layout friction (e.g. `ats-minimal` passes layout checks with 0 penalty, while complex multi-column layouts like `two-column` trigger warnings and parsing friction points).
  - Validates contact email, telephone presence, and date ordering without relying on third-party opaque black-box APIs.
- **Evidence-Grounded Keyword Optimization**:
  - Distinguishes candidate-substantiated keywords from unsupported keywords using `CandidateProfile` evidence.
  - Grounded suggestions recommend natural placement locations (e.g., adding to `skills` array or integrating into relevant work experience bullet points).
  - Strict anti-fabrication safeguard: Unsubstantiated keywords are labeled with prominent warnings explicitly instructing candidates not to invent qualifications.
  - Snapshot isolation: Applying accepted keyword suggestions creates a new independent `CVVersion` snapshot (schema v2.0.0) without mutating the original `CVVersion` or modifying `CandidateProfile`.
- **API Endpoints (`backend/app/api/routes/ats.py`)**:
  - `POST /api/v1/ats/analyze`: Analyzes a selected CV version against an optional job target.
  - `GET /api/v1/ats/cv/{cv_version_id}`: Retrieves ATS analysis with optional `?job_id=` query param.
  - `POST /api/v1/ats/apply-suggestions`: Applies accepted grounded keyword suggestions and returns a new isolated CV version snapshot.
  - Strict ownership checks: Rejects analysis or suggestion application if CV version or job target belongs to another user (403 Forbidden).
- **Frontend User Experience (`frontend`)**:
  - Types & Contracts (`types/ats.ts`): Complete TypeScript interfaces for analysis, component scores, checks, keywords, and suggestions.
  - API & Hooks (`services/ats/ats.api.ts`, `hooks/use-ats.ts`): TanStack Query integration with cache invalidation for CV versions.
  - Component (`components/ats/ats-analysis-view.tsx`):
    - CV Version and Job Target pickers.
    - Radial overall score gauge with color-coded status badges and score tier descriptions.
    - 4 explainable component cards detailing point awards, maximums, and itemized deduction notes.
    - High-signal keyword coverage bar and keyword frequency/density audit table with spam warnings (> 3.5%).
    - Zero-hallucination grounded keyword suggestion cards with accept/reject toggles, evidence snippets, and anti-fabrication warnings.
    - Parser checks filterable by severity (All, Warnings, Passes, Info) covering layout, dates, contact info, headings, and symbols.
    - Optimization Applied modal with immediate routing to CV editor or direct PDF/DOCX downloads.
    - Mandatory heuristic disclaimer banner displayed on all views.
  - Seamless navigation wired into `cv-versions-view.tsx` ("ATS" action button on every version card) and `app/page.tsx` (`ats-analysis` view route).
- **Automated Tests & Quality Verification**:
  - Backend: **88/88 tests passing** (`pytest`) including 7 comprehensive test suites in `test_ats_analysis.py`:
    - `test_ats_analysis_general_baseline`
    - `test_ats_analysis_job_targeted_scoring`
    - `test_ats_keyword_stuffing_detection`
    - `test_ats_template_layout_friction_detection`
    - `test_ats_grounded_vs_unsupported_suggestions`
    - `test_ats_apply_suggestions_snapshot_isolation`
    - `test_ats_cross_user_isolation`
  - Frontend: **90/90 tests passing** (`vitest`) across 16 test suites including `ats-analysis.test.ts`.
  - Type Safety: TypeScript compiler completed with **0 errors** (`npx tsc --noEmit`).
  - Production Build: Next.js Turbopack build compiled successfully in 20.5s with **0 errors** and static page prerendering.

### 2026-10-18 — Phase 7: Evidence-Grounded Cover Letter Generation

- **Domain Model & Persistence (`backend/app/models/cover_letter.py`)**:
  - Independent `CoverLetter(Base, TimestampMixin)` entity stored separately from `CVVersion` snapshots.
  - Associations: `user_id` (foreign key to `users.id`), optional `job_target_id` (foreign key to `job_targets.id`), optional `cv_version_id` (foreign key to `cv_versions.id`).
  - Structured fields: `name`, `status` (draft/ready/archived), `tone` (professional/concise/technical/formal), `length_option` (short/standard/detailed), recipient block (`recipient_name`, `recipient_title`, `recipient_company`, `recipient_address`), salutation, opening, `body_paragraphs` (JSON array of strings), closing, sign-off, sender block (`sender_name`, `sender_contact`), `full_content` (concatenated text representation), `factual_claims` (JSON array of `{claim_text, entity_type, entity_id, verification_status}`), `unresolved_gaps` (JSON array of strings), `change_summary`, `generation_parameters`.
  - Migration `0008_cover_letters.py` created and applied cleanly via Alembic.
  - Bidirectional relationships wired into `User`, `JobTarget`, `CVVersion`, and `models/__init__.py`.
- **Zero-Hallucination Generation Service (`backend/app/services/cover_letter_service.py`)**:
  - Strictly grounds achievements, metrics, technologies, dates, and qualifications against the candidate's master `CandidateProfile` and candidate-confirmed clarification answers.
  - Anti-hallucination isolation: Missing job requirements are extracted into `unresolved_gaps` and expressed with neutral phrasing rather than inventing qualifications.
  - Contextual CV integration: Uses selected `CVVersion` snapshot as optional contextual guidance without mutating the snapshot.
  - Full CRUD & lifecycle operations:
    - `generate_cover_letter`: Validates ownership, extracts evidence facts and gaps, synthesizes grounded structured letter output.
    - `regenerate_cover_letter`: Supports `preserve_as_new_version=True` (creating a new independent draft with preserved version history) or in-place draft regeneration with explainable AI `change_summary`.
    - `update_cover_letter`: Partial edits with automatic recalculation of `full_content`.
    - `duplicate_cover_letter`: Clones an existing letter as an independent new draft.
    - `delete_cover_letter`: Permanent removal.
    - `list_cover_letters`: Filtering by status, job target, search query, and pagination.
- **Multi-Format Export Pipelines (`backend/app/services/export/cover_letter_exporter.py`)**:
  - **PDF Export**: Built with ReportLab using a formal executive letterhead layout, horizontal rule separator, formal date formatting, recipient block, justified paragraphs with proportional leading, signature block, and `NumberedCanvas` page numbering.
  - **DOCX Export**: Built with `python-docx` using standard 1-inch margins, modern typography, proper paragraph spacing (`space_after = Pt(12)`), and formal letterhead structure.
  - Sanitized filenames via `get_sanitized_cover_letter_filename` (e.g. `{Candidate}_{Job}_Cover_Letter.pdf`).
- **REST Endpoints (`backend/app/api/routes/cover_letters.py`)**:
  - `POST /api/v1/cover-letters/generate`: Generate new evidence-grounded cover letter.
  - `GET /api/v1/cover-letters`: List user's cover letters with status, search, and job filters.
  - `GET /api/v1/cover-letters/{id}`: Retrieve single cover letter details.
  - `PUT /api/v1/cover-letters/{id}`: Update draft sections, metadata, and recipient details.
  - `POST /api/v1/cover-letters/{id}/regenerate`: Re-craft letter with version preservation or in-place update.
  - `POST /api/v1/cover-letters/{id}/duplicate`: Clone draft.
  - `DELETE /api/v1/cover-letters/{id}`: Delete letter.
  - `GET /api/v1/cover-letters/{id}/export/pdf`: Download formatted PDF.
  - `GET /api/v1/cover-letters/{id}/export/docx`: Download formatted DOCX.
  - Strict multi-tenant authorization: returns 403 Forbidden on cross-user access attempts.
- **Frontend Architecture & Components (`frontend`)**:
  - Types (`types/cover-letter.ts`): TypeScript interfaces for requests, responses, summaries, tones, lengths, statuses, and factual claim provenance.
  - API & Hooks (`services/cover-letter/cover-letter.api.ts`, `hooks/use-cover-letter.ts`): TanStack Query integration with query key factory `coverLetterKeys` in `lib/query-keys.ts` and automated blob download handling.
  - UI Components (`components/cover-letter/`):
    - `CoverLetterView` (`cover-letter-view.tsx`): Dedicated library with status tabs (All, Drafts, Ready, Archived), real-time search, job target association badges, word counts, and instant PDF/DOCX/Duplicate/Delete actions.
    - `CoverLetterGeneratorModal` (`cover-letter-generator-modal.tsx`): Guided creation modal with JobTarget selector, optional CVVersion selector, tone radio group (professional/concise/technical/formal), length selector (short/standard/detailed), custom instructions, recipient overrides, and Zero-Hallucination Policy banner.
    - `CoverLetterEditor` (`cover-letter-editor.tsx`): Split-screen editing experience with inline title editing, status switcher, dynamic body paragraph manager (add/remove/reorder), live formal paper letterhead preview, and an Evidence & Grounding Audit tab displaying verified claims and missing requirement warnings.
    - `CoverLetterRegenerateModal` (`cover-letter-regenerate-modal.tsx`): Parameter adjustments with "Preserve previous version as a new independent draft" toggle.
  - Route Integration: Connected to `app/page.tsx` under the `cover-email` view route with seamless navigation.
- **Automated Tests & Quality Verification**:
  - Backend: **95/95 tests passing** (`pytest`) including 7 comprehensive Phase 7 test cases in `tests/test_cover_letters.py`:
    - `test_generate_cover_letter_evidence_grounded`
    - `test_generate_cover_letter_with_unresolved_gaps`
    - `test_regenerate_cover_letter_preserves_version_history`
    - `test_regenerate_cover_letter_in_place`
    - `test_cover_letter_crud_and_duplication`
    - `test_cover_letter_cross_user_isolation`
    - `test_cover_letter_pdf_and_docx_export`
  - Frontend: **99/99 tests passing** (`vitest`) across 17 test suites including 9 comprehensive Phase 7 test cases in `__tests__/cover-letter.test.ts`.
  - Type Safety: TypeScript compiler completed with **0 errors** (`npx tsc --noEmit`).
  - Production Build: Next.js Turbopack build compiled successfully with **0 errors** and static page prerendering.

### 2026-10-18 — AI Configuration Hardening & Production Reliability

- **Header-Based Authentication & Credential Secrecy (`backend/app/ai/gemini_provider.py`)**:
  - Replaced URL query string `?key={api_key}` with `x-goog-api-key` HTTP request header across all generation, structured-output, and embedding requests.
  - Request URLs are now clean (`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`), completely eliminating credential leakage in HTTP access logs, proxy traces, and exception traces.
- **Logging Bug & Error Masking Remediation**:
  - Replaced unsupported arbitrary logging keyword arguments (`status_code=...`, `model=...`, `error=...`) with standard f-strings and standard logging formatting.
  - Eliminated `TypeError: Logger._log()` crashes that previously masked underlying API errors.
- **Bounded Retry Policy**:
  - Bounded retries (with exponential backoff) applied strictly to transient failures: HTTP 429 (rate limits), HTTP 5xx (server errors), and network timeouts/disconnects.
  - Immediate failure on non-transient HTTP client errors (400, 401, 403, 404) without useless retries or backoff delays.
- **Production Guardrails & Fail-Fast Validation (`backend/app/core/config.py`, `backend/app/ai/factory.py`)**:
  - In `production` and `staging` environments, `Settings` validation prohibits `AI_PROVIDER='mock'` and disallows silent mock fallback when `AI_PROVIDER='auto'`.
  - When `AI_PROVIDER='gemini'` is explicitly selected, the factory fails fast with an explicit configuration error if `GEMINI_API_KEY` is missing or empty.
  - Added `clear_ai_provider_cache()` to factory to prevent cached provider singletons from retaining stale configuration across test or environment reconfigurations.
- **Safe Readiness Observability (`backend/app/schemas/common.py`, `backend/app/api/routes/health.py`)**:
  - Extended `/api/v1/health/ready` response to include safe, non-sensitive AI metadata (`provider`, `model`, `embedding_model`, `configured`), allowing operators to observe AI status without exposing secret credentials.
- **Environment Documentation (`backend/.env.example`)**:
  - Documented `AI_PROVIDER` options (`auto`, `gemini`, `mock`), `GEMINI_API_KEY`, `GEMINI_MODEL`, and `GEMINI_EMBEDDING_MODEL` with setup instructions.
- **Standalone Smoke-Test Utility (`backend/scripts/verify_gemini.py`)**:
  - CLI script to safely test live Gemini connectivity using header auth and sanitized output without modifying application data.
- **Automated Tests**:
  - Backend: **109/109 tests passing** (`pytest`) with 14 new dedicated test cases in `tests/test_ai_configuration.py` covering header auth, retry policies, production safeguards, and safe health metadata.
  - Frontend: **99/99 tests passing** (`vitest`).

### 2026-10-18 — Phase 8: End-to-End Integration and Production-Readiness Validation

- **Database Schema Drift Remediation & Migration Verification**:
  - Identified 10 schema drift mismatches via `alembic check` between ORM models and Alembic migrations.
  - Added explicit unique constraints and named indexes across `User`, `CandidateProfile`, `CareerPreferences`, `EvidenceAssociation`, `SkillExperienceAssociation`, `SkillProjectAssociation`, `SkillCertificationAssociation`, `SkillAchievementAssociation`, `CVVersion`, and `JobTarget`.
  - Verified migration rollback and upgrade (`alembic downgrade -1` -> `0007_clarification_data` -> `alembic upgrade head` -> `0008_cover_letters`). `alembic check` now outputs `No new upgrade operations detected.` (Zero schema drift).
- **Google Gemini Schema Inlining (`backend/app/ai/gemini_provider.py`)**:
  - Solved Pydantic v2 `$defs` and `$ref` generation incompatibility with Google Gemini REST API. Implemented recursive dereferencing in `_prepare_gemini_schema()`, stripping unsupported OpenAPI metadata keys (`title`, `default`, `$defs`).
  - Improved retry handling on HTTP 429 quota exhaustion and 5xx server errors without credential exposure.
- **Comprehensive End-to-End Integration Test Suite (`backend/tests/test_e2e_integration_journey.py`)**:
  - Implemented and verified the complete 10-step user journey:
    1. Authentication & user isolation setup (`/auth/register`, `/auth/me`).
    2. Master candidate profile + work experience with structured metrics + relational skills linkage + verified evidence item + profile strength check (`/profile/strength`).
    3. Job target creation + automated requirement extraction + grounded candidate matching (`/jobs/{id}/analyze`).
    4. Clarification questions retrieval + candidate answering + candidate profile promotion with verified provenance (`/clarifications/{qid}/promote`).
    5. Evidence-grounded AI CV tailoring with zero-hallucination verification (`/jobs/{id}/tailor-cv`).
    6. Independent CV snapshot editing & immutability verification (confirmed master profile was NOT mutated).
    7. All six CV template configurations + presentation settings + standard clean JSON Resume export (`/json-resume?apply_visibility=true`).
    8. ATS compatibility & explainable keyword scoring + grounded keyword suggestion application vs ungrounded anti-fabrication rejection.
    9. Cover letter generation + editing + saving + new version preservation regeneration + independent duplication.
    10. Multipage PDF exports (CV & cover letter) and DOCX binary exports with zip PK signatures.
    11. Multi-tenant user isolation audit (User B cannot read, update, delete, or export User A's jobs, CV versions, or cover letters).
- **Test Suite Determinism & Production Build**:
  - Configured test isolation in `backend/tests/conftest.py` ensuring fast, deterministic mock provider execution during automated CI/CD runs.
  - Backend: **110 passed, 1 skipped (live free-tier quota exhausted), 0 failed** out of 111 tests.
  - Frontend: **99 passed, 0 failed** out of 99 vitest tests across 17 test suites.
  - TypeScript: **0 errors** (`npx tsc --noEmit`).
  - Production Build: Next.js Turbopack build compiled successfully with **0 errors**.

### 2026-10-20 — Phase 9: Personal Autonomous AI Job Acquisition Agent (Abhijith AT)

- **Domain Models & Database Architecture (`backend/app/models/autonomous_agent.py`)**:
  - Implemented 7 SQLAlchemy 2.x async models with `lazy="selectin"` relationship loading and PostgreSQL JSONB / SQLite JSON cross-compatibility:
    - `JobSearchProfile`: Personal search configuration for Abhijith AT (target roles, locations, experience level, remote preference, daily discovery cap, daily application cap, auto_submit_enabled, emergency_stop).
    - `DiscoveredJob`: Normalized job postings across multi-source adapters with URL hashing deduplication, source provenance (`ats_direct`, `jobicy_api`, `kerala_tech_leads`), match scores, fresher eligibility badges, and explainable evaluation rationale.
    - `QAMemoryBankItem`: Question-answer memory bank for recurring application forms (work authorization, notice period, relocation preferences, salary expectations) with confidence ratings and auto-learning from candidate inputs.
    - `ApplicationRecord`: Full lifecycle tracker for job applications with statuses (`discovered`, `shortlisted`, `tailored`, `prefilled`, `submitted`, `confirmed`, `interview`, `rejected`), submission mode (`supervised`, `autonomous`), confirmation reference numbers, error reasons, and Playwright verification screenshot paths.
    - `RecruiterOutreach`: High-visibility HR outreach generator with channel variants (LinkedIn 300-char note, direct cold email, referral request), outreach status tracking (`drafted`, `pending_review`, `sent`, `replied`), and target job association.
    - `FollowUpSchedule`: Response-aware automated follow-up manager scheduling Day 4 and Day 9 check-ins, auto-canceling on employer response or rejection.
    - `AgentDailyReport`: Morning briefing summaries with run metrics (discovered, shortlisted, applications prepared/submitted, recruiter messages drafted, follow-ups due, unresolved actions).
  - Added Alembic migration `0010_autonomous_agent.py` creating tables, foreign keys, and indexes.
- **Multi-Source Discovery & Fresher-Friendly Evaluation**:
  - Direct ATS adapter (`direct_ats_adapter.py`): Scrapes and parses public Greenhouse and Lever job feeds.
  - Aggregator adapter (`aggregator_adapter.py`): Integrates Jobicy remote developer feeds and Kerala tech companies across Kochi, Kozhikode, and Kannur.
  - Evaluation service (`evaluation_service.py`): Deterministic rules + AI matching tailored for Abhijith AT (MERN Stack, React, Node.js, Express, MongoDB, JavaScript). Recognizes equivalent personal project experience (Portfolio, GitHub) to ensure fresher opportunities are never disqualified merely for lacking multi-year commercial experience.
- **Playwright Application Automation & QA Resolver**:
  - Form automation runner (`playwright_runner.py`): Launches headless Chromium, navigates to application URLs, maps fields heuristically (name, email, phone, LinkedIn, GitHub, portfolio), resolves application questions using `QAMemoryBank`, attaches tailored CV PDF, and captures pre-submission screenshots.
  - Dual Execution Modes: Defaults to **Supervised Mode** (fills form, captures screenshot, awaits 1-click submit approval) with user-configurable **Autonomous Submit** toggle and **Emergency Stop** instant cutoff.
  - Outcome Verification: Verifies submission success, extracts confirmation IDs, and classifies failures.
- **Recruiter Outreach Multiplier & Follow-Up Engine**:
  - Recruiter service (`recruiter_service.py`): Generates grounded, 300-character LinkedIn connection notes and concise cold emails citing actual candidate achievements (e.g., MERN projects) without spam or relationship fabrication.
  - Schedules Day 4 and Day 9 follow-ups that automatically cancel if an employer response or rejection is detected.
- **Daily APScheduler & Orchestration Service**:
  - Autonomous agent service (`autonomous_agent_service.py`): Coordinates full cycle: profile seeding, multi-source discovery, fresher evaluation, automated document tailoring (CV & cover letter), application preparation, outreach drafting, and daily report generation.
  - Background scheduler (`scheduler.py`): APScheduler cron scheduled daily at 07:00 AM IST with lifecycle management in FastAPI lifespan.
- **REST Endpoints (`backend/app/api/routes/autonomous_agent.py`)**:
  - Mounted at `/api/v1/agent`:
    - `GET /profile`, `PUT /profile`: View and edit personal search preferences.
    - `POST /emergency-stop`, `POST /resume`: Instant automation cutoff and resume.
    - `POST /run-cycle`: Trigger full autonomous run immediately.
    - `GET /jobs`: Discovered jobs list with status, role, and location filtering.
    - `POST /jobs/{id}/shortlist`, `POST /jobs/{id}/reject`: Manual curation overrides.
    - `GET /applications`: Applications pipeline tracking with status filters.
    - `POST /applications/{id}/submit`: 1-click supervised submission approval.
    - `GET /qa-bank`, `POST /qa-bank`: View and add QA memory bank items.
    - `GET /outreach`, `POST /outreach/{id}/send`: Recruiter message review and dispatch.
    - `GET /reports/latest`: Latest morning briefing report.
- **Frontend Agent Command Dashboard (`frontend`)**:
  - TypeScript types (`types/agent.ts`) and API client (`services/agent/agent.api.ts`).
  - Agent Dashboard component (`agent-dashboard.tsx`) featuring 6 specialized command views:
    - **Morning Briefing**: Daily agent report with stats cards, top opportunities, and quick action items.
    - **Discovered Jobs**: Real-time job stream with fresher match badges, score breakdown, and shortlist/reject actions.
    - **Applications Pipeline**: Visual tracker with status badges, submission evidence screenshots, and 1-click submit approvals.
    - **Recruiter Outreach Studio**: HR visibility multiplier showing tailored LinkedIn notes and cold email drafts with copy-to-clipboard and dispatch tracking.
    - **QA Memory Bank**: Pre-seeded knowledge repository with Abhijith's confirmed application answers and editor.
    - **Search & Automation Preferences**: Full control over target roles, locations, daily caps, submission mode, and Emergency Stop.
  - App shell navigation updated with "AI Agent" link and robot badge in `app-shell.tsx` and routed in `app/page.tsx`.
- **Automated Tests & Quality Verification**:
  - Backend: **115/115 tests passing** (`pytest`) including 6 comprehensive Phase 9 test cases in `tests/test_autonomous_agent.py`:
    - `test_job_search_profile_defaults_and_update`
    - `test_emergency_stop_and_resume`
    - `test_fresher_friendly_evaluation`
    - `test_qa_memory_bank_resolution`
    - `test_recruiter_outreach_generation_and_length_constraint`
    - `test_full_autonomous_cycle_execution`
  - Frontend: **99/99 tests passing** (`vitest`).
  - TypeScript: **0 errors** (`npx tsc --noEmit`).
  - Production Build: Next.js Turbopack build compiled successfully with **0 errors**.
- **Candidate Relocation & South India Expansion**:
  - Expanded candidate target locations to comprehensively cover South India: **Karnataka** (Bangalore / Bengaluru), **Telangana** (Hyderabad), **Tamil Nadu** (Chennai, Coimbatore), **Kerala** (Kochi, Kozhikode, Kannur, Thiruvananthapuram), and **Remote India**.
  - Synchronized across `JobSearchProfile` model, Pydantic schemas, `QAMemoryBankItem` relocation seeds, evaluation service rules, and aggregator discovery adapter.
  - Added interactive Preferences editor modal/form in `frontend/components/agent/agent-dashboard.tsx` with quick one-click preset buttons for all major South Indian tech hubs.



