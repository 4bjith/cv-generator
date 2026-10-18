import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cv_version import CVVersion
    from app.models.job_target import JobTarget
    from app.models.user import User

# Compatible JSON type across PostgreSQL and SQLite
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class CoverLetter(Base, TimestampMixin):
    """
    Persistent, evidence-grounded Cover Letter artifact.
    Maintains independent provenance and lifecycle from CV versions.
    """

    __tablename__ = "cover_letters"

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
    cv_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("cv_versions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True, nullable=False)
    tone: Mapped[str] = mapped_column(String(50), default="professional", nullable=False)
    length_option: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)

    # Recipient details
    recipient_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    recipient_title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    recipient_company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    recipient_address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    # Structured letter sections
    salutation: Mapped[str] = mapped_column(String(200), default="Dear Hiring Manager,", nullable=False)
    opening: Mapped[str] = mapped_column(Text, nullable=False)
    body_paragraphs: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    closing: Mapped[str] = mapped_column(Text, nullable=False)
    sign_off: Mapped[str] = mapped_column(String(200), default="Sincerely,", nullable=False)

    # Sender info
    sender_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sender_contact: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    # Combined full text representation for quick rendering and search
    full_content: Mapped[str] = mapped_column(Text, nullable=False)

    # Evidence traceability & audit provenance
    factual_claims: Mapped[List[Dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    unresolved_gaps: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generation_parameters: Mapped[Dict[str, Any]] = mapped_column(JSON_TYPE, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="cover_letters",
    )
    job_target: Mapped[Optional["JobTarget"]] = relationship(
        "JobTarget",
        back_populates="cover_letters",
    )
    cv_version: Mapped[Optional["CVVersion"]] = relationship(
        "CVVersion",
        back_populates="cover_letters",
    )

    def __repr__(self) -> str:
        return f"<CoverLetter id={self.id} user_id={self.user_id} name={self.name} status={self.status}>"
