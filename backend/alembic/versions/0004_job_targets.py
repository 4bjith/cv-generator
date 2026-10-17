"""Create job_targets table

Revision ID: 0004_job_targets
Revises: 0003_evidence_and_skills
Create Date: 2026-10-10 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0004_job_targets"
down_revision: Union[str, None] = "0003_evidence_and_skills"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "job_targets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("company_name", sa.String(length=200), nullable=False),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("user_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="saved", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_targets_user_id", "job_targets", ["user_id"], unique=False)
    op.create_index("ix_job_targets_status", "job_targets", ["status"], unique=False)
    op.create_index("ix_job_targets_created_at", "job_targets", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_job_targets_created_at", table_name="job_targets")
    op.drop_index("ix_job_targets_status", table_name="job_targets")
    op.drop_index("ix_job_targets_user_id", table_name="job_targets")
    op.drop_table("job_targets")
