import asyncio
import logging
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous_agent import (
    AgentDailyReport,
    ApplicationRecord,
    DiscoveredJob,
    JobSearchProfile,
)
from app.models.job_target import JobTarget
from app.models.profile import CandidateLink, CandidateProfile
from app.repositories.postgres.autonomous_agent_repository import AutonomousAgentRepository
from app.repositories.postgres.cv_version_repository import PostgresCVVersionRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.repositories.postgres.profile_repository import PostgresProfileRepository
from app.schemas.cover_letter import GenerateCoverLetterRequest
from app.services.application.playwright_runner import PlaywrightApplicationRunner
from app.services.application.qa_resolver import QAResolverService
from app.services.clarification_service import ClarificationService
from app.services.cover_letter_service import CoverLetterService
from app.services.cv_tailoring_service import CVTailoringService
from app.services.discovery.aggregator_adapter import AggregatorDiscoveryAdapter
from app.services.discovery.direct_ats_adapter import DirectATSDiscoveryAdapter
from app.services.discovery.evaluation_service import JobEvaluationService
from app.services.job_intelligence.service import JobIntelligenceService
from app.services.outreach.recruiter_service import RecruiterOutreachService

logger = logging.getLogger(__name__)


class AutonomousJobAgentService:
    """Master orchestrator for the personal autonomous AI career acquisition agent."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AutonomousAgentRepository(db)
        self.profile_repo = PostgresProfileRepository(db)
        self.job_repo = PostgresJobTargetRepository(db)
        self.cv_repo = PostgresCVVersionRepository(db)
        self.clarification_service = ClarificationService(
            job_target_repository=self.job_repo,
            profile_repository=self.profile_repo,
        )
        self.tailoring_service = CVTailoringService(
            job_target_repository=self.job_repo,
            profile_repository=self.profile_repo,
            cv_version_repository=self.cv_repo,
            clarification_service=self.clarification_service,
        )
        self.cover_letter_service = CoverLetterService(session=db)
        self.qa_resolver = QAResolverService(self.repo)
        self.outreach_service = RecruiterOutreachService(self.repo)
        self.playwright_runner = PlaywrightApplicationRunner()
        self.ats_discovery = DirectATSDiscoveryAdapter()
        self.aggregator_discovery = AggregatorDiscoveryAdapter()

    # --------------------------------------------------------------------------
    # Personal Candidate Profile & Search Configuration Seeding
    # --------------------------------------------------------------------------

    async def ensure_personal_configuration(self, user_id: uuid.UUID) -> JobSearchProfile:
        """Ensures Abhijith AT's personal preferences and QA defaults are initialized."""
        south_india_locations = [
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
            "Kozhikode",
            "Kannur",
            "Thiruvananthapuram",
            "Kerala",
            "South India",
        ]

        # 1. Search Profile
        search_profile = await self.repo.get_search_profile(user_id)
        if not search_profile:
            search_profile = await self.repo.create_or_update_search_profile(
                user_id=user_id,
                data={
                    "target_roles": [
                        "MERN Stack Developer",
                        "React Developer",
                        "Full Stack Developer",
                        "Frontend Developer",
                        "Junior Software Engineer",
                        "Node.js Developer",
                        "Web Developer",
                    ],
                    "primary_skills": [
                        "JavaScript",
                        "React",
                        "Node.js",
                        "Express.js",
                        "MongoDB",
                        "REST APIs",
                        "HTML",
                        "CSS",
                        "Git",
                    ],
                    "target_locations": south_india_locations,
                    "is_remote_prioritized": True,
                    "include_internships": True,
                    "fresher_mode": True,
                    "min_salary": 18000,
                    "daily_application_cap": 10,
                    "cron_schedule": "0 7 * * *",
                    "auto_submit_enabled": True,
                    "is_active": True,
                    "emergency_stopped": False,
                },
            )
        else:
            # Synchronize South Indian target locations, full automation, and salary floor
            sync_data = {}
            current_locs = list(search_profile.target_locations or [])
            missing_locs = [loc for loc in south_india_locations if loc not in current_locs]
            if missing_locs:
                sync_data["target_locations"] = current_locs + missing_locs

            if not search_profile.auto_submit_enabled:
                sync_data["auto_submit_enabled"] = True

            if search_profile.min_salary is None or search_profile.min_salary < 18000:
                sync_data["min_salary"] = 18000

            if sync_data:
                search_profile = await self.repo.create_or_update_search_profile(
                    user_id=user_id,
                    data=sync_data,
                )

        # 2. QA Memory Bank Defaults
        await self.qa_resolver.ensure_default_qa_seeds(user_id)

        # 3. Candidate Profile & Links (GitHub, Portfolio, LinkedIn)
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            profile = CandidateProfile(
                user_id=user_id,
                first_name="Abhijith",
                last_name="A T",
                preferred_name="Abhijith",
                email="abhijithatzz@email.com",
                phone="7736 505145",
                professional_headline="Frontend Developer (React.js)",
                primary_title="Frontend Developer (React.js)",
                secondary_titles=["Full Stack Developer (MERN)", "Junior Software Developer", "React Developer"],
                career_level="entry_level",
                industry="Software Development",
                years_of_experience=1.0,
                specializations=["React.js", "Zustand", "Tailwind CSS", "Node.js", "Socket.io", "RESTful APIs"],
                base_summary=(
                    "React.js developer with 6+ months of professional experience as a Junior Software Developer, "
                    "building responsive, performance-minded user interfaces and connecting them to RESTful APIs. "
                    "Worked on AI workflow automation and chatbot platforms, with hands-on use of component-driven architecture, "
                    "state management (Zustand), Tailwind CSS, real-time features (Socket.io) and LLM API integration. "
                    "Also shipped several full applications end to end, including a multi-merchant e-commerce platform "
                    "and a live ride-booking app. Comfortable collaborating with designers and backend developers in a remote, fast-paced setting."
                ),
                city="Kannur",
                state="Kerala",
                country="India",
            )
            self.db.add(profile)
            await self.db.flush()
            await self.db.refresh(profile)

        from sqlalchemy import select
        links_res = await self.db.execute(select(CandidateLink).where(CandidateLink.profile_id == profile.id))
        existing_links = list(links_res.scalars().all())
        existing_urls = {link.url.lower().strip() for link in existing_links if link.url}
        default_links = [
            ("github", "GitHub", "https://github.com/4bjith/"),
            ("portfolio", "Portfolio", "https://4bjith.github.io/Portfolio-Website/"),
            ("linkedin", "LinkedIn", "https://www.linkedin.com/in/abhijith-4bjith/"),
        ]
        for link_type, label, url in default_links:
            if url.lower().strip() not in existing_urls:
                link = CandidateLink(
                    profile_id=profile.id,
                    type=link_type,
                    label=label,
                    url=url,
                    order_index=len(existing_links),
                )
                self.db.add(link)
                existing_links.append(link)
        await self.db.flush()

        return search_profile

    # --------------------------------------------------------------------------
    # Discovery & Evaluation Pipeline
    # --------------------------------------------------------------------------

    async def run_discovery(self, user_id: uuid.UUID) -> List[DiscoveredJob]:
        """Discovers new listings across direct ATS feeds and aggregators, deduplicating and scoring."""
        search_profile = await self.ensure_personal_configuration(user_id)
        candidate_profile = await self.profile_repo.get_by_user_id(user_id)

        # 1. Fetch raw jobs
        ats_jobs = await self.ats_discovery.discover_jobs()
        aggregator_jobs = await self.aggregator_discovery.discover_jobs()
        all_raw_jobs = ats_jobs + aggregator_jobs

        saved_jobs: List[DiscoveredJob] = []

        for raw_job in all_raw_jobs:
            # Calculate unique deduplication hash
            dedup_hash = AutonomousAgentRepository.calculate_dedup_hash(
                source_platform=raw_job.source_platform,
                company_name=raw_job.company_name,
                title=raw_job.title,
                external_id=raw_job.external_id,
            )

            # Check if already discovered
            existing = await self.repo.get_discovered_job_by_dedup(user_id, dedup_hash)
            if existing:
                continue

            # Evaluate fit score & fresher eligibility
            score, eligibility, reasoning = JobEvaluationService.evaluate_job(
                job=raw_job,
                search_profile=search_profile,
                candidate_profile=candidate_profile,
            )

            discovered_entity = DiscoveredJob(
                user_id=user_id,
                search_profile_id=search_profile.id,
                source_platform=raw_job.source_platform,
                external_id=raw_job.external_id,
                dedup_hash=dedup_hash,
                title=raw_job.title,
                company_name=raw_job.company_name,
                location=raw_job.location,
                is_remote=raw_job.is_remote,
                employment_type=raw_job.employment_type,
                source_url=raw_job.source_url,
                apply_url=raw_job.apply_url,
                posted_at=raw_job.posted_at,
                raw_description=raw_job.raw_description,
                extracted_skills=raw_job.extracted_skills,
                match_score=score,
                fit_reasoning=reasoning,
                eligibility_status=eligibility,
                status="shortlisted" if eligibility == "eligible" else "discovered",
            )
            saved = await self.repo.create_discovered_job(discovered_entity)
            saved_jobs.append(saved)

        return saved_jobs

    # --------------------------------------------------------------------------
    # Job Application Preparation & Execution
    # --------------------------------------------------------------------------

    async def prepare_and_process_application(
        self,
        user_id: uuid.UUID,
        discovered_job_id: uuid.UUID,
    ) -> ApplicationRecord:
        """Tailors CV and cover letter, pre-fills portal form via Playwright, drafts recruiter messages."""
        disc_job = await self.repo.get_discovered_job_by_id(discovered_job_id, user_id)
        if not disc_job:
            raise ValueError("Discovered job not found.")

        search_profile = await self.ensure_personal_configuration(user_id)
        candidate_profile = await self.profile_repo.get_by_user_id(user_id)
        if not candidate_profile:
            raise ValueError("Candidate profile must be created before applying.")

        # 1. Promote to JobTarget
        job_target = JobTarget(
            user_id=user_id,
            title=disc_job.title,
            company_name=disc_job.company_name,
            location=disc_job.location,
            employment_type=disc_job.employment_type,
            job_description=disc_job.raw_description,
            source_url=disc_job.source_url,
            status="applied",
            analysis_result={
                "mandatory_requirements": disc_job.extracted_skills,
                "preferred_requirements": ["REST APIs", "Git", "Clean Architecture"],
                "categories": ["frontend", "backend", "fullstack"],
                "keywords": disc_job.extracted_skills,
            },
        )
        self.db.add(job_target)
        await self.db.flush()
        await self.db.refresh(job_target)

        # Link discovered job to the target
        disc_job.job_target_id = job_target.id
        disc_job.status = "tailored"

        # 2. Tailor CV Snapshot
        tailor_res = await self.tailoring_service.tailor_cv(
            user_id=user_id,
            job_id=job_target.id,
        )
        cv_version_id = tailor_res.cv_version_id

        # 3. Generate Cover Letter
        cover_letter_res = await self.cover_letter_service.generate_cover_letter(
            user_id=user_id,
            request=GenerateCoverLetterRequest(
                job_id=job_target.id,
                cv_version_id=cv_version_id,
                name=f"Cover Letter — {disc_job.company_name}",
                tone="professional",
                length_option="standard",
            ),
        )
        cover_letter_id = cover_letter_res.id

        # 4. Create Application Record
        application = ApplicationRecord(
            user_id=user_id,
            discovered_job_id=disc_job.id,
            job_target_id=job_target.id,
            cv_version_id=cv_version_id,
            cover_letter_id=cover_letter_id,
            submission_mode="automated_playwright",
            status="submitting",
        )
        await self.repo.create_application_record(application)

        # 5. Resolve Applicant Form Data
        applicant_data = {
            "first_name": candidate_profile.first_name,
            "last_name": candidate_profile.last_name or "",
            "full_name": f"{candidate_profile.first_name} {candidate_profile.last_name or ''}".strip(),
            "email": candidate_profile.email or "abhijith.dev@example.com",
            "phone": candidate_profile.phone or "+91 9876543210",
            "linkedin_url": "https://www.linkedin.com/in/abhijith-4bjith/",
            "github_url": "https://github.com/4bjith/",
            "portfolio_url": "https://4bjith.github.io/Portfolio-Website/",
        }

        # 6. Execute Playwright Automation
        result = await self.playwright_runner.run_application(
            application_id=application.id,
            apply_url=disc_job.apply_url,
            applicant_data=applicant_data,
            auto_submit=search_profile.auto_submit_enabled,
        )

        # Update application status
        application.status = result.status
        application.portal_confirmation_code = result.confirmation_code
        application.screenshot_url = result.screenshot_path
        application.failure_reason = result.failure_reason
        application.form_answers_submitted = result.form_answers_submitted
        if result.status == "submitted_confirmed":
            application.submitted_at = datetime.now(timezone.utc)
            disc_job.status = "applied"

        await self.db.flush()

        # 7. Prepare Recruiter Outreach & Follow-Ups
        await self.outreach_service.prepare_outreach_for_application(
            application=application,
            job_target=job_target,
            profile=candidate_profile,
        )

        return application

    # --------------------------------------------------------------------------
    # Full Cycle & Daily Report Generation
    # --------------------------------------------------------------------------

    async def run_full_cycle(self, user_id: uuid.UUID, max_applications: int = 3) -> AgentDailyReport:
        """Executes discovery, shortlisting, tailoring, application preparation, and daily briefing."""
        search_profile = await self.ensure_personal_configuration(user_id)
        if search_profile.emergency_stopped:
            raise ValueError("Autonomous agent is currently EMERGENCY STOPPED. Clear the flag in settings to resume.")

        # 1. Discover
        discovered = await self.run_discovery(user_id)

        # 2. Shortlist top eligible jobs
        shortlisted = await self.repo.list_discovered_jobs(
            user_id=user_id,
            status="shortlisted",
            limit=max_applications,
        )

        submitted_count = 0
        prepared_count = 0
        action_items: List[Dict[str, Any]] = []

        for job in shortlisted:
            try:
                app_record = await self.prepare_and_process_application(user_id, job.id)
                if app_record.status == "submitted_confirmed":
                    submitted_count += 1
                else:
                    prepared_count += 1
                    action_items.append({
                        "type": "prepared_application_review",
                        "title": f"{job.title} at {job.company_name}",
                        "apply_url": job.apply_url,
                        "status": app_record.status,
                        "notes": app_record.failure_reason or "Prepared for 1-click candidate submission.",
                    })
            except Exception as exc:
                logger.error(f"Error processing shortlisted job {job.id}: {exc}")
                action_items.append({
                    "type": "application_failure",
                    "title": f"{job.title} at {job.company_name}",
                    "notes": str(exc),
                })

        # 3. Recruiter Outreach Count
        outreach_items = await self.repo.list_recruiter_outreach(user_id, status="drafted")

        # 4. Generate Daily Briefing Markdown
        today = date.today()
        summary_md = f"""# Daily Career Agent Report — {today.strftime('%A, %B %d, %Y')}

### Executive Summary
* **New Jobs Discovered:** {len(discovered)}
* **Eligible Opportunities Shortlisted:** {len(shortlisted)}
* **Applications Confirmed Submitted:** {submitted_count}
* **Applications Prepared (Awaiting Review):** {prepared_count}
* **Recruiter Outreach Drafts Ready:** {len(outreach_items)}

### Best High-Fit Opportunities Today
"""
        for job in shortlisted[:5]:
            summary_md += f"- **{job.title}** at **{job.company_name}** ({job.location}) — Match: `{job.match_score}%`\n  *Rationale:* {job.fit_reasoning}\n"

        if action_items:
            summary_md += "\n### Action Items For You\n"
            for item in action_items:
                summary_md += f"- [{item['title']}]({item.get('apply_url', '#')}): {item['notes']}\n"

        report = AgentDailyReport(
            user_id=user_id,
            run_date=today,
            jobs_discovered_count=len(discovered),
            jobs_shortlisted_count=len(shortlisted),
            applications_submitted_count=submitted_count,
            applications_prepared_count=prepared_count,
            recruiter_outreach_count=len(outreach_items),
            action_items=action_items,
            summary_markdown=summary_md,
        )
        saved_report = await self.repo.create_daily_report(report)
        return saved_report
