"""Add employment_type and analysis_result to job_targets table

Revision ID: 0006_job_analysis
Revises: 0005_cv_versions
Create Date: 2026-10-17 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0006_job_analysis"
down_revision: Union[str, None] = "0005_cv_versions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    op.add_column("job_targets", sa.Column("employment_type", sa.String(length=50), nullable=True))
    op.add_column("job_targets", sa.Column("analysis_result", JSON_TYPE, nullable=True))


def downgrade() -> None:
    op.drop_column("job_targets", "analysis_result")
    op.drop_column("job_targets", "employment_type")
