import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cover_letter import CoverLetter
    from app.models.cv_version import CVVersion
    from app.models.job_target import JobTarget
    from app.models.user import User

JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class JobSearchProfile(Base, TimestampMixin):
    """Personalized job discovery configuration, schedules, and automation rules."""

    __tablename__ = "job_search_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_job_search_profiles_user_id"),
        Index("ix_job_search_profiles_user_id", "user_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Career Preferences
    target_roles: Mapped[List[str]] = mapped_column(
        JSON_TYPE,
        default=lambda: [
            "MERN Stack Developer",
            "React Developer",
            "Full Stack Developer",
            "Frontend Developer",
            "Junior Software Engineer",
            "Node.js Developer",
            "Web Developer",
        ],
        nullable=False,
    )
    primary_skills: Mapped[List[str]] = mapped_column(
        JSON_TYPE,
        default=lambda: [
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
        nullable=False,
    )
    target_locations: Mapped[List[str]] = mapped_column(
        JSON_TYPE,
        default=lambda: [
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
        ],
        nullable=False,
    )
    is_remote_prioritized: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_internships: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fresher_mode: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_job_age_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)

    # Automation Policies & Controls
    daily_application_cap: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    cron_schedule: Mapped[str] = mapped_column(String(50), default="0 7 * * *", nullable=False)
    auto_submit_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    emergency_stopped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="job_search_profile")
    discovered_jobs: Mapped[List["DiscoveredJob"]] = relationship(
        "DiscoveredJob",
        back_populates="search_profile",
        cascade="all, delete-orphan",
    )


class DiscoveredJob(Base, TimestampMixin):
    """External job opportunity discovered by automated source adapters."""

    __tablename__ = "discovered_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "dedup_hash", name="uq_discovered_jobs_user_dedup"),
        Index("ix_discovered_jobs_user_status", "user_id", "status"),
        Index("ix_discovered_jobs_match_score", "match_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    search_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_search_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_target_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Identity & Provenance
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)  # greenhouse, lever, ashby, aggregator
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    dedup_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="Remote", nullable=False)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), default="full_time", nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    apply_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Intelligence & Evaluation
    extracted_skills: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fit_reasoning: Mapped[str] = mapped_column(Text, default="", nullable=False)
    eligibility_status: Mapped[str] = mapped_column(String(50), default="eligible", nullable=False)  # eligible, ineligible, needs_review
    status: Mapped[str] = mapped_column(String(50), default="discovered", nullable=False)  # discovered, shortlisted, tailored, applied, dismissed, rejected_by_rules

    # Relationships
    search_profile: Mapped[Optional["JobSearchProfile"]] = relationship(
        "JobSearchProfile",
        back_populates="discovered_jobs",
    )
    application_record: Mapped[Optional["ApplicationRecord"]] = relationship(
        "ApplicationRecord",
        back_populates="discovered_job",
        uselist=False,
    )


class QAMemoryBankItem(Base, TimestampMixin):
    """Zero-hallucination store for recurring application form questions."""

    __tablename__ = "qa_memory_bank_items"
    __table_args__ = (
        Index("ix_qa_memory_user_category", "user_id", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # work_authorization, notice_period, compensation, relocation, custom
    question_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    answer_value: Mapped[str] = mapped_column(Text, nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class ApplicationRecord(Base, TimestampMixin):
    """End-to-end tracking and audit log for an individual job application."""

    __tablename__ = "application_records"
    __table_args__ = (
        Index("ix_application_records_user_status", "user_id", "status"),
        Index("ix_application_records_job_target", "job_target_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    discovered_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("discovered_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_target_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="CASCADE"),
        nullable=False,
    )
    cv_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cv_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    cover_letter_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cover_letters.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Execution Details
    submission_mode: Mapped[str] = mapped_column(String(50), default="automated_playwright", nullable=False)  # automated_playwright, prepared_manual, api_direct
    status: Mapped[str] = mapped_column(String(50), default="prepared", nullable=False)  # prepared, submitting, submitted_confirmed, submission_failed, requires_human_intervention, screening, interview, offer, rejected, withdrawn
    portal_confirmation_code: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    screenshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    form_answers_submitted: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON_TYPE, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    discovered_job: Mapped[Optional["DiscoveredJob"]] = relationship(
        "DiscoveredJob",
        back_populates="application_record",
        lazy="selectin",
    )
    recruiter_outreach: Mapped[List["RecruiterOutreach"]] = relationship(
        "RecruiterOutreach",
        back_populates="application",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    follow_up_schedules: Mapped[List["FollowUpSchedule"]] = relationship(
        "FollowUpSchedule",
        back_populates="application",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RecruiterOutreach(Base, TimestampMixin):
    """Direct HR, recruiter, or hiring manager outreach contact and drafted message."""

    __tablename__ = "recruiter_outreaches"
    __table_args__ = (
        Index("ix_recruiter_outreaches_user_status", "user_id", "status"),
        Index("ix_recruiter_outreaches_app_id", "application_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("application_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_title: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="linkedin", nullable=False)  # linkedin, email
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message_type: Mapped[str] = mapped_column(String(50), default="connection_note", nullable=False)  # connection_note, recruiter_email, referral_request
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="drafted", nullable=False)  # drafted, approved, sent, replied, closed
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reply_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    application: Mapped["ApplicationRecord"] = relationship(
        "ApplicationRecord",
        back_populates="recruiter_outreach",
    )


class FollowUpSchedule(Base, TimestampMixin):
    """Response-aware automated follow-up calendar event."""

    __tablename__ = "follow_up_schedules"
    __table_args__ = (
        Index("ix_follow_up_schedules_app_status", "application_id", "status"),
        Index("ix_follow_up_schedules_scheduled_for", "scheduled_for"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("application_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1 (Day 4), 2 (Day 9)
    scheduled_for: Mapped[date] = mapped_column(Date, nullable=False)
    follow_up_type: Mapped[str] = mapped_column(String(50), default="receipt_check", nullable=False)
    draft_message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, completed, cancelled_response_received, skipped

    # Relationships
    application: Mapped["ApplicationRecord"] = relationship(
        "ApplicationRecord",
        back_populates="follow_up_schedules",
    )


class AgentDailyReport(Base, TimestampMixin):
    """Daily morning briefing summarizing autonomous pipeline actions and findings."""

    __tablename__ = "agent_daily_reports"
    __table_args__ = (
        Index("ix_agent_daily_reports_user_date", "user_id", "run_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    jobs_discovered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_shortlisted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applications_submitted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applications_prepared_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recruiter_outreach_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    action_items: Mapped[List[Dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    summary_markdown: Mapped[str] = mapped_column(Text, default="", nullable=False)
