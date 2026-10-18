"""Add cover_letters table for evidence-grounded cover letters

Revision ID: 0008_cover_letters
Revises: 0007_clarification_data
Create Date: 2026-10-18 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0008_cover_letters"
down_revision: Union[str, None] = "0007_clarification_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

JSON_TYPE = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    op.create_table(
        "cover_letters",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_target_id", sa.Uuid(as_uuid=True), sa.ForeignKey("job_targets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("cv_version_id", sa.Uuid(as_uuid=True), sa.ForeignKey("cv_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("tone", sa.String(50), nullable=False, server_default="professional"),
        sa.Column("length_option", sa.String(50), nullable=False, server_default="standard"),
        sa.Column("recipient_name", sa.String(200), nullable=True),
        sa.Column("recipient_title", sa.String(200), nullable=True),
        sa.Column("recipient_company", sa.String(200), nullable=True),
        sa.Column("recipient_address", sa.String(300), nullable=True),
        sa.Column("salutation", sa.String(200), nullable=False, server_default="Dear Hiring Manager,"),
        sa.Column("opening", sa.Text(), nullable=False),
        sa.Column("body_paragraphs", JSON_TYPE, nullable=False),
        sa.Column("closing", sa.Text(), nullable=False),
        sa.Column("sign_off", sa.String(200), nullable=False, server_default="Sincerely,"),
        sa.Column("sender_name", sa.String(200), nullable=False),
        sa.Column("sender_contact", sa.String(300), nullable=True),
        sa.Column("full_content", sa.Text(), nullable=False),
        sa.Column("factual_claims", JSON_TYPE, nullable=False),
        sa.Column("unresolved_gaps", JSON_TYPE, nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("generation_parameters", JSON_TYPE, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_cover_letters_user_id", "cover_letters", ["user_id"])
    op.create_index("ix_cover_letters_job_target_id", "cover_letters", ["job_target_id"])
    op.create_index("ix_cover_letters_cv_version_id", "cover_letters", ["cv_version_id"])
    op.create_index("ix_cover_letters_status", "cover_letters", ["status"])


def downgrade() -> None:
    op.drop_index("ix_cover_letters_status", table_name="cover_letters")
    op.drop_index("ix_cover_letters_cv_version_id", table_name="cover_letters")
    op.drop_index("ix_cover_letters_job_target_id", table_name="cover_letters")
    op.drop_index("ix_cover_letters_user_id", table_name="cover_letters")
    op.drop_table("cover_letters")
