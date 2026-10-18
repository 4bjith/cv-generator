import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.auth_session import AuthSession
    from app.models.cover_letter import CoverLetter
    from app.models.cv_version import CVVersion
    from app.models.job_target import JobTarget
    from app.models.profile import CandidateProfile


class User(Base, TimestampMixin):
    """User account entity representing a registered candidate."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    auth_sessions: Mapped[List["AuthSession"]] = relationship(
        "AuthSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    candidate_profile: Mapped[Optional["CandidateProfile"]] = relationship(
        "CandidateProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    job_targets: Mapped[List["JobTarget"]] = relationship(
        "JobTarget",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    cv_versions: Mapped[List["CVVersion"]] = relationship(
        "CVVersion",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    cover_letters: Mapped[List["CoverLetter"]] = relationship(
        "CoverLetter",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} is_active={self.is_active}>"
