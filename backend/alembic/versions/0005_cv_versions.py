"""Create cv_versions table

Revision ID: 0005_cv_versions
Revises: 0004_job_targets
Create Date: 2026-10-10 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0005_cv_versions"
down_revision: Union[str, None] = "0004_job_targets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    op.create_table(
        "cv_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("job_target_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=50), server_default="draft", nullable=False),
        sa.Column("content_snapshot", JSON_TYPE, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_target_id"], ["job_targets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cv_versions_user_id", "cv_versions", ["user_id"], unique=False)
    op.create_index("ix_cv_versions_job_target_id", "cv_versions", ["job_target_id"], unique=False)
    op.create_index("ix_cv_versions_status", "cv_versions", ["status"], unique=False)
    op.create_index("ix_cv_versions_created_at", "cv_versions", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cv_versions_created_at", table_name="cv_versions")
    op.drop_index("ix_cv_versions_status", table_name="cv_versions")
    op.drop_index("ix_cv_versions_job_target_id", table_name="cv_versions")
    op.drop_index("ix_cv_versions_user_id", table_name="cv_versions")
    op.drop_table("cv_versions")
