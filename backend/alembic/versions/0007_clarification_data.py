"""Add clarification_data to job_targets table

Revision ID: 0007_clarification_data
Revises: 0006_job_analysis
Create Date: 2026-10-18 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0007_clarification_data"
down_revision: Union[str, None] = "0006_job_analysis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    op.add_column("job_targets", sa.Column("clarification_data", JSON_TYPE, nullable=True))


def downgrade() -> None:
    op.drop_column("job_targets", "clarification_data")
