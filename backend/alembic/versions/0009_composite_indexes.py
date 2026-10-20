"""Add composite indexes for job targets and CV versions

Revision ID: 0009_composite_indexes
Revises: 0008_cover_letters
Create Date: 2026-10-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0009_composite_indexes"
down_revision: Union[str, None] = "0008_cover_letters"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_job_targets_user_id_created_at",
        "job_targets",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_cv_versions_user_id_created_at",
        "cv_versions",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_cv_versions_user_id_created_at", table_name="cv_versions")
    op.drop_index("ix_job_targets_user_id_created_at", table_name="job_targets")
