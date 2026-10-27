from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.models.autonomous_agent import ApplicationRecord, FollowUpSchedule, RecruiterOutreach
from app.models.job_target import JobTarget
from app.models.profile import CandidateProfile
from app.repositories.postgres.autonomous_agent_repository import AutonomousAgentRepository


class RecruiterOutreachService:
    """Generates personalized, high-conversion recruiter outreach messages and schedules follow-ups."""

    def __init__(self, repo: AutonomousAgentRepository):
        self.repo = repo

    def generate_linkedin_connection_note(
        self,
        candidate_name: str,
        recruiter_name: str,
        role_title: str,
        company_name: str,
        highlight_skill_or_project: str = "MERN Stack applications",
    ) -> str:
        """
        Drafts a concise LinkedIn connection note strictly within LinkedIn's 300-character limit.
        """
        first_name = recruiter_name.split()[0] if recruiter_name else "there"
        note = (
            f"Hi {first_name}, I recently applied for the {role_title} role at {company_name}. "
            f"I build full-stack web solutions with {highlight_skill_or_project} and verified projects on GitHub. "
            f"I'd love to connect and follow your team's work!"
        )
        if len(note) > 300:
            note = note[:297] + "..."
        return note

    def generate_recruiter_email(
        self,
        candidate_name: str,
        recruiter_name: str,
        role_title: str,
        company_name: str,
        portfolio_url: str = "https://4bjith.github.io/Portfolio-Website/",
        github_url: str = "https://github.com/4bjith/",
    ) -> str:
        """
        Drafts an executive, concise recruiter email (< 120 words).
        """
        first_name = recruiter_name.split()[0] if recruiter_name else "Hiring Team"
        body = (
            f"Dear {first_name},\n\n"
            f"I recently submitted my application for the {role_title} opening at {company_name}.\n\n"
            f"As an early-career developer specializing in the MERN stack (React, Node.js, Express, MongoDB), "
            f"I focus on writing clean, maintainable code and building responsive web applications. "
            f"You can view my live deployed projects on my portfolio ({portfolio_url}) and inspect my source code on GitHub ({github_url}).\n\n"
            f"I welcome the opportunity to discuss how my background aligns with your team's goals.\n\n"
            f"Best regards,\n{candidate_name}"
        )
        return body

    async def prepare_outreach_for_application(
        self,
        application: ApplicationRecord,
        job_target: JobTarget,
        profile: CandidateProfile,
    ) -> List[RecruiterOutreach]:
        """Identifies target outreach contacts and prepares message drafts for candidate review."""
        existing = await self.repo.list_recruiter_outreach(application.user_id)
        existing_company_contacts = {o.company_name.lower(): o for o in existing if o.company_name}

        company = job_target.company_name or "Target Company"
        if company.lower() in existing_company_contacts:
            return []

        recruiter_name = f"Talent Team at {company}"
        recruiter_title = "Technical Recruiter / Talent Acquisition"
        candidate_full_name = f"{profile.first_name} {profile.last_name or ''}".strip() or "Abhijith AT"

        # 1. Draft LinkedIn Connection Note
        linkedin_note = self.generate_linkedin_connection_note(
            candidate_name=candidate_full_name,
            recruiter_name="Talent Lead",
            role_title=job_target.title,
            company_name=company,
            highlight_skill_or_project="React, Node.js, and MongoDB",
        )
        outreach_linkedin = RecruiterOutreach(
            user_id=application.user_id,
            application_id=application.id,
            company_name=company,
            contact_name=recruiter_name,
            contact_title=recruiter_title,
            channel="linkedin",
            profile_url=f"https://www.linkedin.com/company/{company.lower().replace(' ', '-')}/people/",
            message_type="connection_note",
            message_content=linkedin_note,
            status="drafted",
        )
        await self.repo.create_recruiter_outreach(outreach_linkedin)

        # 2. Draft Executive Email
        email_body = self.generate_recruiter_email(
            candidate_name=candidate_full_name,
            recruiter_name="Hiring Team",
            role_title=job_target.title,
            company_name=company,
        )
        outreach_email = RecruiterOutreach(
            user_id=application.user_id,
            application_id=application.id,
            company_name=company,
            contact_name=recruiter_name,
            contact_title=recruiter_title,
            channel="email",
            email=f"careers@{company.lower().replace(' ', '')}.com",
            message_type="recruiter_email",
            message_content=email_body,
            status="drafted",
        )
        await self.repo.create_recruiter_outreach(outreach_email)

        # 3. Schedule Response-Aware Follow-Ups (Day 4 & Day 9)
        today = date.today()
        day_4 = today + timedelta(days=4)
        day_9 = today + timedelta(days=9)

        follow_up_1 = FollowUpSchedule(
            application_id=application.id,
            step_number=1,
            scheduled_for=day_4,
            follow_up_type="receipt_check",
            draft_message=(
                f"Hi team, just following up on my application for the {job_target.title} position submitted on {today.strftime('%b %d')}. "
                f"Please let me know if any additional details are needed."
            ),
            status="pending",
        )
        await self.repo.create_follow_up(follow_up_1)

        follow_up_2 = FollowUpSchedule(
            application_id=application.id,
            step_number=2,
            scheduled_for=day_9,
            follow_up_type="project_share",
            draft_message=(
                f"Hi team, wanted to share an update on a recent project relevant to your stack: "
                f"https://4bjith.github.io/Portfolio-Website/ . Looking forward to hearing if there might be a mutual fit!"
            ),
            status="pending",
        )
        await self.repo.create_follow_up(follow_up_2)

        return [outreach_linkedin, outreach_email]
