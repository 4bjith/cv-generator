import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User

# Use JSON type which works across Postgres and SQLite testing
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class CandidateProfile(Base, TimestampMixin):
    """Candidate master career knowledge base entity."""

    __tablename__ = "candidate_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_candidate_profiles_user_id"),
        Index("ix_candidate_profiles_user_id", "user_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Identity
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    preferred_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    professional_headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    profile_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Contact Info
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Professional Identity
    primary_title: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    secondary_titles: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    career_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    years_of_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    specializations: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)

    # Professional Summary
    base_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="candidate_profile",
    )
    links: Mapped[List["CandidateLink"]] = relationship(
        "CandidateLink",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="CandidateLink.order_index",
    )
    experiences: Mapped[List["WorkExperience"]] = relationship(
        "WorkExperience",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="WorkExperience.order_index",
    )
    education: Mapped[List["EducationRecord"]] = relationship(
        "EducationRecord",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="EducationRecord.order_index",
    )
    skills: Mapped[List["CandidateSkill"]] = relationship(
        "CandidateSkill",
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Project.order_index",
    )
    certifications: Mapped[List["Certification"]] = relationship(
        "Certification",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Certification.order_index",
    )
    achievements: Mapped[List["Achievement"]] = relationship(
        "Achievement",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Achievement.order_index",
    )
    languages: Mapped[List["CandidateLanguage"]] = relationship(
        "CandidateLanguage",
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    career_preferences: Mapped[Optional["CareerPreferences"]] = relationship(
        "CareerPreferences",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
    )
    evidence_items: Mapped[List["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CandidateProfile id={self.id} user_id={self.user_id} name={self.first_name} {self.last_name}>"


class CandidateLink(Base, TimestampMixin):
    """External professional links (GitHub, LinkedIn, Portfolio, etc.)."""

    __tablename__ = "candidate_links"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="links")


class WorkExperience(Base, TimestampMixin):
    """Work experience record entity."""

    __tablename__ = "work_experiences"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(50), default="full_time", nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    start_date: Mapped[str] = mapped_column(String(50), nullable=False)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    achievements: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    technologies: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    metrics: Mapped[List[Dict[str, Any]]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="experiences")
    skill_associations: Mapped[List["SkillExperienceAssociation"]] = relationship(
        "SkillExperienceAssociation",
        back_populates="experience",
        cascade="all, delete-orphan",
    )


class EducationRecord(Base, TimestampMixin):
    """Academic and formal education record entity."""

    __tablename__ = "education_records"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(200), nullable=False)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    achievements: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="education")


class CandidateSkill(Base, TimestampMixin):
    """Skills and competencies entity."""

    __tablename__ = "candidate_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    proficiency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    years_of_experience: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_references: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="skills")
    experience_associations: Mapped[List["SkillExperienceAssociation"]] = relationship(
        "SkillExperienceAssociation",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    project_associations: Mapped[List["SkillProjectAssociation"]] = relationship(
        "SkillProjectAssociation",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    certification_associations: Mapped[List["SkillCertificationAssociation"]] = relationship(
        "SkillCertificationAssociation",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    achievement_associations: Mapped[List["SkillAchievementAssociation"]] = relationship(
        "SkillAchievementAssociation",
        back_populates="skill",
        cascade="all, delete-orphan",
    )


class Project(Base, TimestampMixin):
    """Personal, open-source, or professional projects entity."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    problem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    achievements: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    technologies: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    architecture: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    team_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    live_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    repository_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="projects")
    skill_associations: Mapped[List["SkillProjectAssociation"]] = relationship(
        "SkillProjectAssociation",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Certification(Base, TimestampMixin):
    """Professional certifications and licenses entity."""

    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[str] = mapped_column(String(200), nullable=False)
    issue_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    expiration_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    credential_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    credential_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    skills: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="certifications")
    skill_associations: Mapped[List["SkillCertificationAssociation"]] = relationship(
        "SkillCertificationAssociation",
        back_populates="certification",
        cascade="all, delete-orphan",
    )


class Achievement(Base, TimestampMixin):
    """Independent achievements, awards, and honors entity."""

    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    issuer: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    evidence_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="achievements")
    skill_associations: Mapped[List["SkillAchievementAssociation"]] = relationship(
        "SkillAchievementAssociation",
        back_populates="achievement",
        cascade="all, delete-orphan",
    )


class CandidateLanguage(Base, TimestampMixin):
    """Language proficiencies entity."""

    __tablename__ = "candidate_languages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[str] = mapped_column(String(50), nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="languages")


class CareerPreferences(Base, TimestampMixin):
    """Candidate job search and workplace preferences entity."""

    __tablename__ = "career_preferences"
    __table_args__ = (
        UniqueConstraint("profile_id", name="uq_career_preferences_profile_id"),
        Index("ix_career_preferences_profile_id", "profile_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_roles: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    target_industries: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    preferred_locations: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    remote_preference: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employment_types: Mapped[List[str]] = mapped_column(JSON_TYPE, default=list, nullable=False)
    availability_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    available_from: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notice_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="career_preferences")


# ==========================================
# Phase 1.1: Evidence & Provenance Models
# ==========================================

class EvidenceItem(Base, TimestampMixin):
    """First-class evidence record backing candidate claims and facts."""

    __tablename__ = "evidence_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="link", nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(50), default="unverified", nullable=False)
    provenance: Mapped[str] = mapped_column(String(50), default="user_provided", nullable=False)

    profile: Mapped["CandidateProfile"] = relationship("CandidateProfile", back_populates="evidence_items")
    associations: Mapped[List["EvidenceAssociation"]] = relationship(
        "EvidenceAssociation",
        back_populates="evidence",
        cascade="all, delete-orphan",
    )


class EvidenceAssociation(Base, TimestampMixin):
    """Generic polymorphic-like association link between EvidenceItem and profile entities."""

    __tablename__ = "evidence_associations"
    __table_args__ = (
        UniqueConstraint("evidence_id", "entity_type", "entity_id", name="uq_evidence_associations_evidence_entity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("evidence_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)

    evidence: Mapped["EvidenceItem"] = relationship("EvidenceItem", back_populates="associations")


# ==========================================
# Phase 1.1: Skill Relationship Link Tables
# ==========================================

class SkillExperienceAssociation(Base, TimestampMixin):
    """Link table connecting a Skill to a Work Experience."""

    __tablename__ = "skill_experiences"
    __table_args__ = (
        UniqueConstraint("skill_id", "experience_id", name="uq_skill_experiences_skill_exp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    experience_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("work_experiences.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    skill: Mapped["CandidateSkill"] = relationship("CandidateSkill", back_populates="experience_associations")
    experience: Mapped["WorkExperience"] = relationship("WorkExperience", back_populates="skill_associations")


class SkillProjectAssociation(Base, TimestampMixin):
    """Link table connecting a Skill to a Project."""

    __tablename__ = "skill_projects"
    __table_args__ = (
        UniqueConstraint("skill_id", "project_id", name="uq_skill_projects_skill_proj"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    skill: Mapped["CandidateSkill"] = relationship("CandidateSkill", back_populates="project_associations")
    project: Mapped["Project"] = relationship("Project", back_populates="skill_associations")


class SkillCertificationAssociation(Base, TimestampMixin):
    """Link table connecting a Skill to a Certification."""

    __tablename__ = "skill_certifications"
    __table_args__ = (
        UniqueConstraint("skill_id", "certification_id", name="uq_skill_certifications_skill_cert"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    certification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("certifications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    skill: Mapped["CandidateSkill"] = relationship("CandidateSkill", back_populates="certification_associations")
    certification: Mapped["Certification"] = relationship("Certification", back_populates="skill_associations")


class SkillAchievementAssociation(Base, TimestampMixin):
    """Link table connecting a Skill to an Achievement."""

    __tablename__ = "skill_achievements"
    __table_args__ = (
        UniqueConstraint("skill_id", "achievement_id", name="uq_skill_achievements_skill_ach"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("candidate_skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    skill: Mapped["CandidateSkill"] = relationship("CandidateSkill", back_populates="achievement_associations")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="skill_associations")

