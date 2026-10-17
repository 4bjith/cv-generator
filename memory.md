# AI CV Maker — Development Memory

**Last updated:** 2026-10-02  
**Project status:** Frontend and backend foundation scaffold complete; product feature development has not started.

## Purpose

AI CV Maker is an AI-powered job application assistant. It maintains a structured, evidence-backed professional profile for a candidate, understands a target job, compares job requirements with verified candidate evidence, asks for missing information, and generates tailored application materials.

The product is not only a resume generator. Its differentiator is the intersection of:

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

Generated content must be truthful, ATS-friendly, editable, versioned, and traceable to candidate evidence.

## Source documentation

- [`FRD.md`](./FRD.md) — complete product requirements and MVP definition.
- [`CODING_AGENT_CONTEXT.md`](./CODING_AGENT_CONTEXT.md) — architecture, implementation rules, security principles, and agent behavior.

## Non-negotiable product rules

1. Never fabricate experience, skills, technologies, projects, education, achievements, metrics, or responsibilities.
2. Treat the database-backed Candidate Knowledge Base as the source of truth; the LLM is an intelligence layer, not the database.
3. Use evidence states (`OBSERVED`, `USER_CONFIRMED`, `INFERRED`, `UNKNOWN`) and do not turn weak or unknown evidence into factual claims.
4. Ask the user when information is missing or ambiguous.
5. Keep AI-generated content editable and do not silently modify permanent profile data.
6. Keep Gemini behind an internal provider abstraction with configurable model names.
7. Do not build automatic job application submission for the MVP.

## Target architecture

- Frontend: Next.js, TypeScript, App Router, Tailwind CSS, shadcn/ui, TanStack Query, React Hook Form, Zod.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, Pytest.
- Data and infrastructure: PostgreSQL + pgvector, Redis, S3-compatible storage, Docker.
- AI: Google Gemini through an internal `AIProvider` interface for text, structured output, vision, embeddings, and token counting.
- Backend layering: API → service → repository → database. AI belongs in services, not route handlers.

## MVP feature map

| Area | Status | Notes |
| --- | --- | --- |
| Repository scaffolding | Complete | Next.js frontend and layered FastAPI backend are available and validated. |
| Frontend foundation | Complete | Next.js 16.3.8 App Router with TypeScript, Tailwind CSS, ESLint, and npm. |
| Backend foundation | Complete | FastAPI 0.142.2 with versioned `/api/v1/health`, structured JSON logging, correlation IDs, centralized exception handling, security middlewares, Dockerfile, and pytest suite. |
| Authentication foundation | Complete | JWT access/refresh token pairs, bcrypt hashing, stateless API routes (`/api/v1/auth/{register,login,me,refresh,logout}`), `get_current_user` dependency, and repository pattern abstraction. |
| Candidate profile / Knowledge Base | Complete | Master career knowledge base domain model, PostgreSQL schema with Alembic migration, normalized child entities, structured metrics, ProfileService, readiness scoring, TanStack Query integration, and full-stack responsive UI. |
| CV import and parsing | Not started | PDF, DOCX, TXT, and image inputs; preserve original files; require review before persistence. |
| GitHub integration | Not started | OAuth, selective repository analysis, project extraction, and evidence mapping. |
| Job input and analysis | Complete | Saved job targets with full CRUD, employment type capture, modular extraction pipeline (mandatory vs preferred, seniority, categories, keywords), and validation. |
| Requirement matching | Complete | Canonical `JobRequirementItem`, evidence-grounded matching against candidate knowledge base, strict non-hallucination, full evidence traceability, gap distinction, and non-mutating CV version snapshot creation. |
| Clarification engine | Not started | Minimal, relevant questions for missing evidence; confirmed answers may update the profile. |
| CV generation and ATS analysis | Not started | Structured CV JSON first, then template rendering; no ATS guarantee claims. |
| Cover email / cover letter | Not started | Must use the same verified evidence as the CV. |
| Recruiter message | Not started | LinkedIn, recruiter outreach, and referral variants. |
| Interview preparation | Not started | Job-specific technical, project, experience, behavioral, and company questions. |
| Application tracker | Not started | Status history, notes, dates, job data, and document versions. |
| Versioning and auditability | Not started | Do not overwrite generated artifacts; retain relevant source/model/timestamp metadata. |
| Testing and production hardening | Not started | Unit, integration, API, frontend, AI schema/evaluation, security, observability, and deployment work. |

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
