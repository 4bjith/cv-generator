"""Add evidence items, evidence associations, skill relational links, and provenance columns

Revision ID: 0003_evidence_and_skills
Revises: 0002_candidate_profile
Create Date: 2026-10-06 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_evidence_and_skills"
down_revision: Union[str, None] = "0002_candidate_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add provenance column to profile entities
    op.add_column(
        "work_experiences",
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
    )
    op.add_column(
        "education_records",
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
    )
    op.add_column(
        "candidate_skills",
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
    )
    op.add_column(
        "projects",
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
    )
    op.add_column(
        "certifications",
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
    )
    op.add_column(
        "achievements",
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
    )

    # 2. evidence_items
    op.create_table(
        "evidence_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("profile_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), server_default="link", nullable=False),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("date", sa.String(length=50), nullable=True),
        sa.Column("verification_status", sa.String(length=50), server_default="unverified", nullable=False),
        sa.Column("provenance", sa.String(length=50), server_default="user_provided", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["profile_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evidence_items_profile_id", "evidence_items", ["profile_id"], unique=False)

    # 3. evidence_associations
    op.create_table(
        "evidence_associations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evidence_id", "entity_type", "entity_id", name="uq_evidence_associations_evidence_entity"),
    )
    op.create_index("ix_evidence_associations_evidence_id", "evidence_associations", ["evidence_id"], unique=False)
    op.create_index("ix_evidence_associations_entity_type", "evidence_associations", ["entity_type"], unique=False)
    op.create_index("ix_evidence_associations_entity_id", "evidence_associations", ["entity_id"], unique=False)

    # 4. skill_experiences
    op.create_table(
        "skill_experiences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("experience_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["candidate_skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["experience_id"], ["work_experiences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_id", "experience_id", name="uq_skill_experiences_skill_exp"),
    )
    op.create_index("ix_skill_experiences_skill_id", "skill_experiences", ["skill_id"], unique=False)
    op.create_index("ix_skill_experiences_experience_id", "skill_experiences", ["experience_id"], unique=False)

    # 5. skill_projects
    op.create_table(
        "skill_projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["candidate_skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_id", "project_id", name="uq_skill_projects_skill_proj"),
    )
    op.create_index("ix_skill_projects_skill_id", "skill_projects", ["skill_id"], unique=False)
    op.create_index("ix_skill_projects_project_id", "skill_projects", ["project_id"], unique=False)

    # 6. skill_certifications
    op.create_table(
        "skill_certifications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("certification_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["candidate_skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["certification_id"], ["certifications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_id", "certification_id", name="uq_skill_certifications_skill_cert"),
    )
    op.create_index("ix_skill_certifications_skill_id", "skill_certifications", ["skill_id"], unique=False)
    op.create_index("ix_skill_certifications_certification_id", "skill_certifications", ["certification_id"], unique=False)

    # 7. skill_achievements
    op.create_table(
        "skill_achievements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.Uuid(), nullable=False),
        sa.Column("achievement_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["skill_id"], ["candidate_skills.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["achievement_id"], ["achievements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_id", "achievement_id", name="uq_skill_achievements_skill_ach"),
    )
    op.create_index("ix_skill_achievements_skill_id", "skill_achievements", ["skill_id"], unique=False)
    op.create_index("ix_skill_achievements_achievement_id", "skill_achievements", ["achievement_id"], unique=False)


def downgrade() -> None:
    op.drop_table("skill_achievements")
    op.drop_table("skill_certifications")
    op.drop_table("skill_projects")
    op.drop_table("skill_experiences")
    op.drop_table("evidence_associations")
    op.drop_table("evidence_items")
    op.drop_column("achievements", "provenance")
    op.drop_column("certifications", "provenance")
    op.drop_column("projects", "provenance")
    op.drop_column("candidate_skills", "provenance")
    op.drop_column("education_records", "provenance")
    op.drop_column("work_experiences", "provenance")
