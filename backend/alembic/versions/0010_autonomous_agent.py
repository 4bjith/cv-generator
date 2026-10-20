"""Add autonomous agent models: job search profiles, discovered jobs, QA bank, application records, recruiter outreaches, follow-ups, daily reports

Revision ID: 0010_autonomous_agent
Revises: 0009_composite_indexes
Create Date: 2026-10-20 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0010_autonomous_agent"
down_revision: Union[str, None] = "0009_composite_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB, "postgresql")


def upgrade() -> None:
    # 1. job_search_profiles
    op.create_table(
        "job_search_profiles",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_roles", JSON_TYPE, nullable=False),
        sa.Column("primary_skills", JSON_TYPE, nullable=False),
        sa.Column("target_locations", JSON_TYPE, nullable=False),
        sa.Column("is_remote_prioritized", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("include_internships", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("fresher_mode", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("min_salary", sa.Integer(), nullable=True),
        sa.Column("max_job_age_days", sa.Integer(), server_default=sa.text("7"), nullable=False),
        sa.Column("daily_application_cap", sa.Integer(), server_default=sa.text("10"), nullable=False),
        sa.Column("cron_schedule", sa.String(50), server_default="0 7 * * *", nullable=False),
        sa.Column("auto_submit_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("emergency_stopped", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_job_search_profiles_user_id"),
    )
    op.create_index("ix_job_search_profiles_user_id", "job_search_profiles", ["user_id"], unique=True)

    # 2. discovered_jobs
    op.create_table(
        "discovered_jobs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("search_profile_id", sa.Uuid(as_uuid=True), sa.ForeignKey("job_search_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("job_target_id", sa.Uuid(as_uuid=True), sa.ForeignKey("job_targets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_platform", sa.String(50), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("dedup_hash", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), server_default="Remote", nullable=False),
        sa.Column("is_remote", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("employment_type", sa.String(50), server_default="full_time", nullable=False),
        sa.Column("source_url", sa.String(1000), nullable=False),
        sa.Column("apply_url", sa.String(1000), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("extracted_skills", JSON_TYPE, nullable=False),
        sa.Column("match_score", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("fit_reasoning", sa.Text(), server_default="", nullable=False),
        sa.Column("eligibility_status", sa.String(50), server_default="eligible", nullable=False),
        sa.Column("status", sa.String(50), server_default="discovered", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "dedup_hash", name="uq_discovered_jobs_user_dedup"),
    )
    op.create_index("ix_discovered_jobs_user_status", "discovered_jobs", ["user_id", "status"])
    op.create_index("ix_discovered_jobs_match_score", "discovered_jobs", ["match_score"])

    # 3. qa_memory_bank_items
    op.create_table(
        "qa_memory_bank_items",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("question_pattern", sa.String(255), nullable=False),
        sa.Column("answer_value", sa.Text(), nullable=False),
        sa.Column("is_confirmed", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("user_notes", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_qa_memory_user_category", "qa_memory_bank_items", ["user_id", "category"])

    # 4. application_records
    op.create_table(
        "application_records",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("discovered_job_id", sa.Uuid(as_uuid=True), sa.ForeignKey("discovered_jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("job_target_id", sa.Uuid(as_uuid=True), sa.ForeignKey("job_targets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cv_version_id", sa.Uuid(as_uuid=True), sa.ForeignKey("cv_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cover_letter_id", sa.Uuid(as_uuid=True), sa.ForeignKey("cover_letters.id", ondelete="SET NULL"), nullable=True),
        sa.Column("submission_mode", sa.String(50), server_default="automated_playwright", nullable=False),
        sa.Column("status", sa.String(50), server_default="prepared", nullable=False),
        sa.Column("portal_confirmation_code", sa.String(255), nullable=True),
        sa.Column("screenshot_url", sa.String(500), nullable=True),
        sa.Column("form_answers_submitted", JSON_TYPE, nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_application_records_user_status", "application_records", ["user_id", "status"])
    op.create_index("ix_application_records_job_target", "application_records", ["job_target_id"])

    # 5. recruiter_outreaches
    op.create_table(
        "recruiter_outreaches",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("application_id", sa.Uuid(as_uuid=True), sa.ForeignKey("application_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("contact_name", sa.String(255), nullable=False),
        sa.Column("contact_title", sa.String(255), nullable=False),
        sa.Column("channel", sa.String(50), server_default="linkedin", nullable=False),
        sa.Column("profile_url", sa.String(500), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("message_type", sa.String(50), server_default="connection_note", nullable=False),
        sa.Column("message_content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default="drafted", nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reply_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_recruiter_outreaches_user_status", "recruiter_outreaches", ["user_id", "status"])
    op.create_index("ix_recruiter_outreaches_app_id", "recruiter_outreaches", ["application_id"])

    # 6. follow_up_schedules
    op.create_table(
        "follow_up_schedules",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("application_id", sa.Uuid(as_uuid=True), sa.ForeignKey("application_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step_number", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("scheduled_for", sa.Date(), nullable=False),
        sa.Column("follow_up_type", sa.String(50), server_default="receipt_check", nullable=False),
        sa.Column("draft_message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_follow_up_schedules_app_status", "follow_up_schedules", ["application_id", "status"])
    op.create_index("ix_follow_up_schedules_scheduled_for", "follow_up_schedules", ["scheduled_for"])

    # 7. agent_daily_reports
    op.create_table(
        "agent_daily_reports",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column("jobs_discovered_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("jobs_shortlisted_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("applications_submitted_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("applications_prepared_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("recruiter_outreach_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("action_items", JSON_TYPE, nullable=False),
        sa.Column("summary_markdown", sa.Text(), server_default="", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_agent_daily_reports_user_date", "agent_daily_reports", ["user_id", "run_date"])


def downgrade() -> None:
    op.drop_table("agent_daily_reports")
    op.drop_table("follow_up_schedules")
    op.drop_table("recruiter_outreaches")
    op.drop_table("application_records")
    op.drop_table("qa_memory_bank_items")
    op.drop_table("discovered_jobs")
    op.drop_table("job_search_profiles")
