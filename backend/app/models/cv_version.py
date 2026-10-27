import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import ForeignKey, Index, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cover_letter import CoverLetter
    from app.models.job_target import JobTarget
    from app.models.user import User

# Compatible JSON type across PostgreSQL and SQLite
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class CVVersion(Base, TimestampMixin):
    """Persistent CV version with independent content snapshot derived from CandidateProfile."""

    __tablename__ = "cv_versions"
    __table_args__ = (
        Index("ix_cv_versions_created_at", "created_at"),
        Index("ix_cv_versions_user_id_created_at", "user_id", "created_at"),
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
    job_target_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_targets.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True, nullable=False)
    content_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="cv_versions",
    )
    job_target: Mapped[Optional["JobTarget"]] = relationship(
        "JobTarget",
        back_populates="cv_versions",
    )
    cover_letters: Mapped[List["CoverLetter"]] = relationship(
        "CoverLetter",
        back_populates="cv_version",
    )

    def __repr__(self) -> str:
        return f"<CVVersion id={self.id} user_id={self.user_id} name={self.name} status={self.status}>"
