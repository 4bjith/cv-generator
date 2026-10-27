import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# Job Search Profile Schemas
# ==============================================================================

class JobSearchProfileBase(BaseModel):
    target_roles: List[str] = Field(
        default_factory=lambda: [
            "MERN Stack Developer",
            "React Developer",
            "Full Stack Developer",
            "Frontend Developer",
            "Junior Software Engineer",
            "Node.js Developer",
            "Web Developer",
        ]
    )
    primary_skills: List[str] = Field(
        default_factory=lambda: [
            "JavaScript",
            "React",
            "Node.js",
            "Express.js",
            "MongoDB",
            "REST APIs",
            "HTML",
            "CSS",
            "Git",
        ]
    )
    target_locations: List[str] = Field(
        default_factory=lambda: [
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
    )
    is_remote_prioritized: bool = True
    include_internships: bool = True
    fresher_mode: bool = True
    min_salary: Optional[int] = 18000
    max_job_age_days: int = 7
    daily_application_cap: int = 10
    cron_schedule: str = "0 7 * * *"
    auto_submit_enabled: bool = True
    is_active: bool = True
    emergency_stopped: bool = False


class JobSearchProfileCreate(JobSearchProfileBase):
    pass


class JobSearchProfileUpdate(BaseModel):
    target_roles: Optional[List[str]] = None
    primary_skills: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    is_remote_prioritized: Optional[bool] = None
    include_internships: Optional[bool] = None
    fresher_mode: Optional[bool] = None
    min_salary: Optional[int] = None
    max_job_age_days: Optional[int] = None
    daily_application_cap: Optional[int] = None
    cron_schedule: Optional[str] = None
    auto_submit_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    emergency_stopped: Optional[bool] = None


class JobSearchProfileResponse(JobSearchProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Discovered Job Schemas
# ==============================================================================

class DiscoveredJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    search_profile_id: Optional[uuid.UUID] = None
    job_target_id: Optional[uuid.UUID] = None
    source_platform: str
    external_id: str
    title: str
    company_name: str
    location: str
    is_remote: bool
    employment_type: str
    source_url: str
    apply_url: str
    posted_at: Optional[datetime] = None
    raw_description: str
    extracted_skills: List[str] = Field(default_factory=list)
    match_score: float
    fit_reasoning: str
    eligibility_status: str
    status: str
    created_at: datetime


# ==============================================================================
# QA Memory Bank Schemas
# ==============================================================================

class QAMemoryBankItemCreate(BaseModel):
    category: str
    question_pattern: str
    answer_value: str
    is_confirmed: bool = True
    user_notes: Optional[str] = None


class QAMemoryBankItemUpdate(BaseModel):
    question_pattern: Optional[str] = None
    answer_value: Optional[str] = None
    is_confirmed: Optional[bool] = None
    user_notes: Optional[str] = None


class QAMemoryBankItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    question_pattern: str
    answer_value: str
    is_confirmed: bool
    user_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ==============================================================================
# Recruiter Outreach Schemas
# ==============================================================================

class RecruiterOutreachResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    application_id: uuid.UUID
    company_name: str
    contact_name: str
    contact_title: str
    channel: str
    profile_url: Optional[str] = None
    email: Optional[str] = None
    message_type: str
    message_content: str
    status: str
    sent_at: Optional[datetime] = None
    reply_notes: Optional[str] = None
    created_at: datetime


class RecruiterOutreachUpdate(BaseModel):
    message_content: Optional[str] = None
    status: Optional[str] = None
    reply_notes: Optional[str] = None


# ==============================================================================
# Follow-Up Schedule Schemas
# ==============================================================================

class FollowUpScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    step_number: int
    scheduled_for: date
    follow_up_type: str
    draft_message: str
    status: str
    created_at: datetime


# ==============================================================================
# Application Record Schemas
# ==============================================================================

class ApplicationRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    discovered_job_id: Optional[uuid.UUID] = None
    job_target_id: uuid.UUID
    cv_version_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None
    submission_mode: str
    status: str
    portal_confirmation_code: Optional[str] = None
    screenshot_url: Optional[str] = None
    form_answers_submitted: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None
    submitted_at: Optional[datetime] = None
    last_status_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    recruiter_outreach: List[RecruiterOutreachResponse] = Field(default_factory=list)
    follow_up_schedules: List[FollowUpScheduleResponse] = Field(default_factory=list)


class ApplicationRecordUpdate(BaseModel):
    status: Optional[str] = None
    portal_confirmation_code: Optional[str] = None
    failure_reason: Optional[str] = None


# ==============================================================================
# Daily Report & Pipeline Run Schemas
# ==============================================================================

class AgentDailyReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    run_date: date
    jobs_discovered_count: int
    jobs_shortlisted_count: int
    applications_submitted_count: int
    applications_prepared_count: int
    recruiter_outreach_count: int
    action_items: List[Dict[str, Any]] = Field(default_factory=list)
    summary_markdown: str
    created_at: datetime


class AgentRunResult(BaseModel):
    status: str
    message: str
    jobs_found: int
    jobs_shortlisted: int
    applications_prepared: int
    applications_submitted: int
    recruiter_messages_drafted: int
    report: Optional[AgentDailyReportResponse] = None
