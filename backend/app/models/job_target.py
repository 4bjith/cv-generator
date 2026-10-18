import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cover_letter import CoverLetter
    from app.models.cv_version import CVVersion
    from app.models.user import User

# Compatible JSON type across PostgreSQL and SQLite
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class JobTarget(Base, TimestampMixin):
    """Job target / opportunity entity created and tracked by a candidate."""

    __tablename__ = "job_targets"
    __table_args__ = (
        Index("ix_job_targets_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="saved", index=True, nullable=False)
    analysis_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON_TYPE, nullable=True)
    clarification_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON_TYPE, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="job_targets",
    )
    cv_versions: Mapped[List["CVVersion"]] = relationship(
        "CVVersion",
        back_populates="job_target",
    )
    cover_letters: Mapped[List["CoverLetter"]] = relationship(
        "CoverLetter",
        back_populates="job_target",
    )

    def __repr__(self) -> str:
        return f"<JobTarget id={self.id} user_id={self.user_id} title={self.title} company={self.company_name} status={self.status}>"
