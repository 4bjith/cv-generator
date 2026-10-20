import hashlib
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.autonomous_agent import (
    AgentDailyReport,
    ApplicationRecord,
    DiscoveredJob,
    FollowUpSchedule,
    JobSearchProfile,
    QAMemoryBankItem,
    RecruiterOutreach,
)


class AutonomousAgentRepository:
    """Repository handling all database interactions for the personal autonomous career agent."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------------------------------
    # JobSearchProfile
    # --------------------------------------------------------------------------

    async def get_search_profile(self, user_id: uuid.UUID) -> Optional[JobSearchProfile]:
        query = select(JobSearchProfile).where(JobSearchProfile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_or_update_search_profile(
        self, user_id: uuid.UUID, data: Dict[str, Any]
    ) -> JobSearchProfile:
        profile = await self.get_search_profile(user_id)
        if profile is None:
            profile = JobSearchProfile(user_id=user_id, **data)
            self.db.add(profile)
        else:
            for key, value in data.items():
                if value is not None and hasattr(profile, key):
                    setattr(profile, key, value)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    # --------------------------------------------------------------------------
    # DiscoveredJob
    # --------------------------------------------------------------------------

    @staticmethod
    def calculate_dedup_hash(source_platform: str, company_name: str, title: str, external_id: str) -> str:
        raw_key = f"{source_platform.strip().lower()}:{company_name.strip().lower()}:{title.strip().lower()}:{external_id.strip().lower()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    async def get_discovered_job_by_dedup(self, user_id: uuid.UUID, dedup_hash: str) -> Optional[DiscoveredJob]:
        query = select(DiscoveredJob).where(
            DiscoveredJob.user_id == user_id,
            DiscoveredJob.dedup_hash == dedup_hash,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_discovered_job(self, job: DiscoveredJob) -> DiscoveredJob:
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def list_discovered_jobs(
        self,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        eligibility: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DiscoveredJob]:
        query = select(DiscoveredJob).where(DiscoveredJob.user_id == user_id)
        if status:
            query = query.where(DiscoveredJob.status == status)
        if eligibility:
            query = query.where(DiscoveredJob.eligibility_status == eligibility)
        query = query.order_by(desc(DiscoveredJob.match_score), desc(DiscoveredJob.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_discovered_job_by_id(self, job_id: uuid.UUID, user_id: uuid.UUID) -> Optional[DiscoveredJob]:
        query = select(DiscoveredJob).where(
            DiscoveredJob.id == job_id,
            DiscoveredJob.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_discovered_job_status(
        self,
        job_id: uuid.UUID,
        user_id: uuid.UUID,
        status: str,
        job_target_id: Optional[uuid.UUID] = None,
    ) -> Optional[DiscoveredJob]:
        job = await self.get_discovered_job_by_id(job_id, user_id)
        if not job:
            return None
        job.status = status
        if job_target_id:
            job.job_target_id = job_target_id
        await self.db.flush()
        await self.db.refresh(job)
        return job

    # --------------------------------------------------------------------------
    # QAMemoryBankItem
    # --------------------------------------------------------------------------

    async def list_qa_items(self, user_id: uuid.UUID, category: Optional[str] = None) -> List[QAMemoryBankItem]:
        query = select(QAMemoryBankItem).where(QAMemoryBankItem.user_id == user_id)
        if category:
            query = query.where(QAMemoryBankItem.category == category)
        query = query.order_by(QAMemoryBankItem.category, QAMemoryBankItem.question_pattern)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_qa_item(self, item: QAMemoryBankItem) -> QAMemoryBankItem:
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def get_qa_item(self, item_id: uuid.UUID, user_id: uuid.UUID) -> Optional[QAMemoryBankItem]:
        query = select(QAMemoryBankItem).where(
            QAMemoryBankItem.id == item_id,
            QAMemoryBankItem.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_qa_item(self, item_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = delete(QAMemoryBankItem).where(
            QAMemoryBankItem.id == item_id,
            QAMemoryBankItem.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def find_matching_qa_answer(self, user_id: uuid.UUID, question_text: str) -> Optional[QAMemoryBankItem]:
        """Finds matching verified answer for a portal question using deterministic keyword matching."""
        items = await self.list_qa_items(user_id)
        norm_q = question_text.strip().lower()
        for item in items:
            pattern = item.question_pattern.strip().lower()
            if pattern in norm_q or norm_q in pattern:
                return item
        return None

    # --------------------------------------------------------------------------
    # ApplicationRecord
    # --------------------------------------------------------------------------

    async def create_application_record(self, record: ApplicationRecord) -> ApplicationRecord:
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def get_application_record(self, record_id: uuid.UUID, user_id: uuid.UUID) -> Optional[ApplicationRecord]:
        query = select(ApplicationRecord).where(
            ApplicationRecord.id == record_id,
            ApplicationRecord.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_application_records(
        self,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ApplicationRecord]:
        query = select(ApplicationRecord).where(ApplicationRecord.user_id == user_id)
        if status:
            query = query.where(ApplicationRecord.status == status)
        query = query.order_by(desc(ApplicationRecord.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_application_status(
        self,
        record_id: uuid.UUID,
        user_id: uuid.UUID,
        status: str,
        portal_confirmation_code: Optional[str] = None,
        failure_reason: Optional[str] = None,
        screenshot_url: Optional[str] = None,
    ) -> Optional[ApplicationRecord]:
        record = await self.get_application_record(record_id, user_id)
        if not record:
            return None
        record.status = status
        if portal_confirmation_code is not None:
            record.portal_confirmation_code = portal_confirmation_code
        if failure_reason is not None:
            record.failure_reason = failure_reason
        if screenshot_url is not None:
            record.screenshot_url = screenshot_url
        if status == "submitted_confirmed" and not record.submitted_at:
            record.submitted_at = datetime.now(timezone.utc)
        record.last_status_checked_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    # --------------------------------------------------------------------------
    # RecruiterOutreach
    # --------------------------------------------------------------------------

    async def create_recruiter_outreach(self, outreach: RecruiterOutreach) -> RecruiterOutreach:
        self.db.add(outreach)
        await self.db.flush()
        await self.db.refresh(outreach)
        return outreach

    async def list_recruiter_outreach(
        self,
        user_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> List[RecruiterOutreach]:
        query = select(RecruiterOutreach).where(RecruiterOutreach.user_id == user_id)
        if status:
            query = query.where(RecruiterOutreach.status == status)
        query = query.order_by(desc(RecruiterOutreach.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recruiter_outreach(self, outreach_id: uuid.UUID, user_id: uuid.UUID) -> Optional[RecruiterOutreach]:
        query = select(RecruiterOutreach).where(
            RecruiterOutreach.id == outreach_id,
            RecruiterOutreach.user_id == user_id,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_outreach_status(
        self,
        outreach_id: uuid.UUID,
        user_id: uuid.UUID,
        status: str,
        reply_notes: Optional[str] = None,
    ) -> Optional[RecruiterOutreach]:
        outreach = await self.get_recruiter_outreach(outreach_id, user_id)
        if not outreach:
            return None
        outreach.status = status
        if reply_notes is not None:
            outreach.reply_notes = reply_notes
        if status == "sent" and not outreach.sent_at:
            outreach.sent_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(outreach)
        return outreach

    # --------------------------------------------------------------------------
    # FollowUpSchedule
    # --------------------------------------------------------------------------

    async def create_follow_up(self, follow_up: FollowUpSchedule) -> FollowUpSchedule:
        self.db.add(follow_up)
        await self.db.flush()
        await self.db.refresh(follow_up)
        return follow_up

    async def list_pending_follow_ups(self, check_date: date) -> List[FollowUpSchedule]:
        query = select(FollowUpSchedule).where(
            FollowUpSchedule.scheduled_for <= check_date,
            FollowUpSchedule.status == "pending",
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # --------------------------------------------------------------------------
    # AgentDailyReport
    # --------------------------------------------------------------------------

    async def create_daily_report(self, report: AgentDailyReport) -> AgentDailyReport:
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def get_latest_daily_report(self, user_id: uuid.UUID) -> Optional[AgentDailyReport]:
        query = select(AgentDailyReport).where(
            AgentDailyReport.user_id == user_id
        ).order_by(desc(AgentDailyReport.run_date), desc(AgentDailyReport.created_at)).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_daily_reports(self, user_id: uuid.UUID, limit: int = 14) -> List[AgentDailyReport]:
        query = select(AgentDailyReport).where(
            AgentDailyReport.user_id == user_id
        ).order_by(desc(AgentDailyReport.run_date)).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
