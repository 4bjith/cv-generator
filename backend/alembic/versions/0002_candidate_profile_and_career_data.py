"""Create candidate profile and normalized career data tables

Revision ID: 0002_candidate_profile
Revises: 0001_initial
Create Date: 2026-10-05 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0002_candidate_profile"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    # 1. candidate_profiles
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("preferred_name", sa.String(length=100), nullable=True),
        sa.Column("professional_headline", sa.String(length=255), nullable=True),
        sa.Column("profile_photo", sa.String(length=500), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("country_code", sa.String(length=10), nullable=True),
        sa.Column("primary_title", sa.String(length=150), nullable=True),
        sa.Column("secondary_titles", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("career_level", sa.String(length=50), nullable=True),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("years_of_experience", sa.Float(), nullable=True),
        sa.Column("specializations", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("base_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_candidate_profiles_user_id"),
    )
    op.create_index("ix_candidate_profiles_user_id", "candidate_profiles", ["user_id"], unique=True)

    # 2. candidate_links
    op.create_table(
        "candidate_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_links_profile_id", "candidate_links", ["profile_id"], unique=False)

    # 3. work_experiences
    op.create_table(
        "work_experiences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("company", sa.String(length=200), nullable=False),
        sa.Column("position", sa.String(length=200), nullable=False),
        sa.Column("employment_type", sa.String(length=50), server_default="full_time", nullable=False),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("start_date", sa.String(length=50), nullable=False),
        sa.Column("end_date", sa.String(length=50), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("responsibilities", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("achievements", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("technologies", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("metrics", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_work_experiences_profile_id", "work_experiences", ["profile_id"], unique=False)

    # 4. education_records
    op.create_table(
        "education_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("institution", sa.String(length=200), nullable=False),
        sa.Column("degree", sa.String(length=200), nullable=False),
        sa.Column("field_of_study", sa.String(length=200), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("start_date", sa.String(length=50), nullable=True),
        sa.Column("end_date", sa.String(length=50), nullable=True),
        sa.Column("grade", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("achievements", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_education_records_profile_id", "education_records", ["profile_id"], unique=False)

    # 5. candidate_skills
    op.create_table(
        "candidate_skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("proficiency", sa.String(length=50), nullable=True),
        sa.Column("years_of_experience", sa.Float(), nullable=True),
        sa.Column("last_used", sa.String(length=50), nullable=True),
        sa.Column("evidence_references", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_skills_profile_id", "candidate_skills", ["profile_id"], unique=False)

    # 6. projects
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=150), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("problem", sa.Text(), nullable=True),
        sa.Column("solution", sa.Text(), nullable=True),
        sa.Column("responsibilities", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("achievements", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("technologies", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("architecture", sa.Text(), nullable=True),
        sa.Column("start_date", sa.String(length=50), nullable=True),
        sa.Column("end_date", sa.String(length=50), nullable=True),
        sa.Column("team_size", sa.Integer(), nullable=True),
        sa.Column("live_url", sa.String(length=500), nullable=True),
        sa.Column("repository_url", sa.String(length=500), nullable=True),
        sa.Column("featured", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_profile_id", "projects", ["profile_id"], unique=False)

    # 7. certifications
    op.create_table(
        "certifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("issuer", sa.String(length=200), nullable=False),
        sa.Column("issue_date", sa.String(length=50), nullable=True),
        sa.Column("expiration_date", sa.String(length=50), nullable=True),
        sa.Column("credential_id", sa.String(length=100), nullable=True),
        sa.Column("credential_url", sa.String(length=500), nullable=True),
        sa.Column("skills", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_certifications_profile_id", "certifications", ["profile_id"], unique=False)

    # 8. achievements
    op.create_table(
        "achievements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date", sa.String(length=50), nullable=True),
        sa.Column("issuer", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("evidence_url", sa.String(length=500), nullable=True),
        sa.Column("order_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_achievements_profile_id", "achievements", ["profile_id"], unique=False)

    # 9. candidate_languages
    op.create_table(
        "candidate_languages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("proficiency", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_languages_profile_id", "candidate_languages", ["profile_id"], unique=False)

    # 10. career_preferences
    op.create_table(
        "career_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("target_roles", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("target_industries", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("preferred_locations", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("remote_preference", sa.String(length=50), nullable=True),
        sa.Column("employment_types", JSON_TYPE, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("availability_status", sa.String(length=50), nullable=True),
        sa.Column("available_from", sa.String(length=50), nullable=True),
        sa.Column("notice_period_days", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", name="uq_career_preferences_profile_id"),
    )
    op.create_index("ix_career_preferences_profile_id", "career_preferences", ["profile_id"], unique=True)


def downgrade() -> None:
    op.drop_table("career_preferences")
    op.drop_table("candidate_languages")
    op.drop_table("achievements")
    op.drop_table("certifications")
    op.drop_table("projects")
    op.drop_table("candidate_skills")
    op.drop_table("education_records")
    op.drop_table("work_experiences")
    op.drop_table("candidate_links")
    op.drop_table("candidate_profiles")
