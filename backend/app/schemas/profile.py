from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


# ==========================================
# Enumerations
# ==========================================

class CareerLevel(str, Enum):
    STUDENT = "student"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    TEMPORARY = "temporary"
    VOLUNTEER = "volunteer"
    OTHER = "other"


class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    CLOUD = "cloud"
    DEVOPS = "devops"
    TESTING = "testing"
    AI_ML = "ai_ml"
    DESIGN = "design"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    DOMAIN = "domain"
    OTHER = "other"


class SkillProficiency(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LanguageProficiency(str, Enum):
    BASIC = "basic"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    FLUENT = "fluent"
    NATIVE = "native"


class RemotePreference(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    FLEXIBLE = "flexible"


class AvailabilityStatus(str, Enum):
    ACTIVELY_LOOKING = "actively_looking"
    OPEN_TO_OPPORTUNITIES = "open_to_opportunities"
    NOT_LOOKING = "not_looking"


class AchievementCategory(str, Enum):
    HACKATHON = "hackathon"
    AWARD = "award"
    COMPETITION = "competition"
    SCHOLARSHIP = "scholarship"
    OPEN_SOURCE = "open_source"
    PUBLICATION = "publication"
    CONFERENCE = "conference"
    LEADERSHIP = "leadership"
    COMMUNITY = "community"
    OTHER = "other"


class ProvenanceType(str, Enum):
    USER_PROVIDED = "user_provided"
    AI_GENERATED = "ai_generated"
    AI_ENHANCED = "ai_enhanced"
    IMPORTED = "imported"


class EvidenceSourceType(str, Enum):
    LINK = "link"
    DOCUMENT = "document"
    REPOSITORY = "repository"
    RECOMMENDATION = "recommendation"
    METRIC_REPORT = "metric_report"
    CREDENTIAL = "credential"
    OTHER = "other"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    SELF_ATTESTED = "self_attested"
    THIRD_PARTY_CONFIRMED = "third_party_confirmed"


class LinkType(str, Enum):
    GITHUB = "github"
    LINKEDIN = "linkedin"
    PORTFOLIO = "portfolio"
    WEBSITE = "website"
    BEHANCE = "behance"
    DRIBBBLE = "dribbble"
    STACKOVERFLOW = "stackoverflow"
    KAGGLE = "kaggle"
    MEDIUM = "medium"
    OTHER = "other"


# ==========================================
# Link Schemas
# ==========================================

class LinkCreate(BaseModel):
    type: str = Field(default="other", description="Platform type e.g. github, linkedin, portfolio")
    label: str = Field(min_length=1, max_length=100, description="Display label e.g. GitHub")
    url: str = Field(min_length=3, max_length=500, description="Destination URL")
    order_index: int = 0

    @field_validator("label", "type", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v_strip = v.strip()
        if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v_strip


class LinkUpdate(BaseModel):
    type: Optional[str] = None
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = Field(None, min_length=3, max_length=500)
    order_index: Optional[int] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("URL must start with http:// or https://")
            return v_strip
        return v


class LinkResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    type: str
    label: str
    url: str
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Work Experience Schemas
# ==========================================

class ExperienceMetric(BaseModel):
    value: Union[float, int, str]
    unit: str
    description: str


class WorkExperienceCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    employment_type: str = Field(default="full_time")
    location: Optional[str] = None
    start_date: str = Field(min_length=1, max_length=50, description="Start date (YYYY-MM or YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, max_length=50, description="End date (nullable if current)")
    is_current: bool = False
    description: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    metrics: List[ExperienceMetric] = Field(default_factory=list)
    provenance: Optional[str] = Field(default="user_provided")
    order_index: int = 0

    @field_validator("company", "position", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "WorkExperienceCreate":
        if not self.is_current and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date.")
        return self


class WorkExperienceUpdate(BaseModel):
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    position: Optional[str] = Field(None, min_length=1, max_length=200)
    employment_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = Field(None, min_length=1, max_length=50)
    end_date: Optional[str] = Field(None, max_length=50)
    is_current: Optional[bool] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    metrics: Optional[List[ExperienceMetric]] = None
    provenance: Optional[str] = None
    order_index: Optional[int] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "WorkExperienceUpdate":
        if self.is_current is False and self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date.")
        return self


class WorkExperienceResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    company: str
    position: str
    employment_type: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    is_current: bool
    description: Optional[str] = None
    responsibilities: List[str]
    achievements: List[str]
    technologies: List[str]
    metrics: List[Dict[str, Any]]
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Education Schemas
# ==========================================

class EducationCreate(BaseModel):
    institution: str = Field(min_length=1, max_length=200)
    degree: str = Field(min_length=1, max_length=200)
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)
    provenance: Optional[str] = Field(default="user_provided")
    order_index: int = 0

    @field_validator("institution", "degree", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> "EducationCreate":
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date.")
        return self


class EducationUpdate(BaseModel):
    institution: Optional[str] = Field(None, min_length=1, max_length=200)
    degree: Optional[str] = Field(None, min_length=1, max_length=200)
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    provenance: Optional[str] = None
    order_index: Optional[int] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "EducationUpdate":
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date.")
        return self


class EducationResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    achievements: List[str]
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Skill Schemas
# ==========================================

class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_of_experience: Optional[float] = Field(None, ge=0)
    last_used: Optional[str] = None
    evidence_references: List[str] = Field(default_factory=list)
    provenance: Optional[str] = Field(default="user_provided")
    experience_ids: List[uuid.UUID] = Field(default_factory=list)
    project_ids: List[uuid.UUID] = Field(default_factory=list)
    certification_ids: List[uuid.UUID] = Field(default_factory=list)
    achievement_ids: List[uuid.UUID] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_of_experience: Optional[float] = Field(None, ge=0)
    last_used: Optional[str] = None
    evidence_references: Optional[List[str]] = None
    provenance: Optional[str] = None
    experience_ids: Optional[List[uuid.UUID]] = None
    project_ids: Optional[List[uuid.UUID]] = None
    certification_ids: Optional[List[uuid.UUID]] = None
    achievement_ids: Optional[List[uuid.UUID]] = None


class SkillRelationshipsUpdate(BaseModel):
    experience_ids: Optional[List[uuid.UUID]] = None
    project_ids: Optional[List[uuid.UUID]] = None
    certification_ids: Optional[List[uuid.UUID]] = None
    achievement_ids: Optional[List[uuid.UUID]] = None


class SkillResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_of_experience: Optional[float] = None
    last_used: Optional[str] = None
    evidence_references: List[str]
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    experience_ids: List[uuid.UUID] = Field(default_factory=list)
    project_ids: List[uuid.UUID] = Field(default_factory=list)
    certification_ids: List[uuid.UUID] = Field(default_factory=list)
    achievement_ids: List[uuid.UUID] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Project Schemas
# ==========================================

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    architecture: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_size: Optional[int] = Field(None, ge=1)
    live_url: Optional[str] = None
    repository_url: Optional[str] = None
    featured: bool = False
    provenance: Optional[str] = Field(default="user_provided")
    order_index: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("live_url", "repository_url")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Project URL must start with http:// or https://")
            return v_strip
        return None

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectCreate":
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date.")
        return self


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    architecture: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_size: Optional[int] = Field(None, ge=1)
    live_url: Optional[str] = None
    repository_url: Optional[str] = None
    featured: Optional[bool] = None
    provenance: Optional[str] = None
    order_index: Optional[int] = None

    @field_validator("live_url", "repository_url")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Project URL must start with http:// or https://")
            return v_strip
        return None

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectUpdate":
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot precede start_date.")
        return self


class ProjectResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    responsibilities: List[str]
    achievements: List[str]
    technologies: List[str]
    architecture: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_size: Optional[int] = None
    live_url: Optional[str] = None
    repository_url: Optional[str] = None
    featured: bool
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Certification Schemas
# ==========================================

class CertificationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    issuer: str = Field(min_length=1, max_length=200)
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    provenance: Optional[str] = Field(default="user_provided")
    order_index: int = 0

    @field_validator("name", "issuer", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("credential_url")
    @classmethod
    def validate_credential_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Credential URL must start with http:// or https://")
            return v_strip
        return None


class CertificationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    issuer: Optional[str] = Field(None, min_length=1, max_length=200)
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    skills: Optional[List[str]] = None
    provenance: Optional[str] = None
    order_index: Optional[int] = None

    @field_validator("credential_url")
    @classmethod
    def validate_credential_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Credential URL must start with http:// or https://")
            return v_strip
        return None


class CertificationResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    name: str
    issuer: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    skills: List[str]
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Achievement Schemas
# ==========================================

class AchievementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None
    category: Optional[str] = None
    evidence_url: Optional[str] = None
    provenance: Optional[str] = Field(default="user_provided")
    order_index: int = 0

    @field_validator("title", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("evidence_url")
    @classmethod
    def validate_evidence_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Evidence URL must start with http:// or https://")
            return v_strip
        return None


class AchievementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None
    category: Optional[str] = None
    evidence_url: Optional[str] = None
    provenance: Optional[str] = None
    order_index: Optional[int] = None

    @field_validator("evidence_url")
    @classmethod
    def validate_evidence_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Evidence URL must start with http:// or https://")
            return v_strip
        return None


class AchievementResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    title: str
    description: Optional[str] = None
    date: Optional[str] = None
    issuer: Optional[str] = None
    category: Optional[str] = None
    evidence_url: Optional[str] = None
    provenance: str = "user_provided"
    evidence_ids: List[uuid.UUID] = Field(default_factory=list)
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Phase 1.1: Evidence Schemas
# ==========================================

class EvidenceAssociationCreate(BaseModel):
    entity_type: str = Field(description="Target entity type: experience, project, skill, achievement, certification, education")
    entity_id: uuid.UUID

    @field_validator("entity_type")
    @classmethod
    def validate_entity_type(cls, v: str) -> str:
        valid_types = {"experience", "project", "skill", "achievement", "certification", "education"}
        v_clean = v.strip().lower()
        if v_clean not in valid_types:
            raise ValueError(f"entity_type must be one of: {', '.join(sorted(valid_types))}")
        return v_clean


class EvidenceAssociationResponse(BaseModel):
    id: uuid.UUID
    evidence_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Brief descriptive evidence title")
    description: Optional[str] = None
    source: str = Field(min_length=1, max_length=100, description="Origin source e.g. GitHub Repo, Client Letter, Production Log")
    source_type: str = Field(default="link", description="Source type e.g. link, repository, credential, document, recommendation, metric_report, other")
    url: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None
    verification_status: str = Field(default="unverified", description="unverified, verified, self_attested, third_party_confirmed")
    provenance: str = Field(default="user_provided", description="user_provided, ai_generated, ai_enhanced, imported")
    associated_entities: List[EvidenceAssociationCreate] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_associations(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "associations" in data and not data.get("associated_entities"):
                data["associated_entities"] = data["associations"]
        return data

    @field_validator("title", "source", mode="before")
    @classmethod
    def strip_text(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("URL must start with http:// or https://")
            return v_strip
        return None


class EvidenceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    source: Optional[str] = Field(None, min_length=1, max_length=100)
    source_type: Optional[str] = None
    url: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None
    verification_status: Optional[str] = None
    provenance: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("URL must start with http:// or https://")
            return v_strip
        return None


class EvidenceResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    title: str
    description: Optional[str] = None
    source: str
    source_type: str
    url: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None
    verification_status: str
    provenance: str
    associations: List[EvidenceAssociationResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)



# ==========================================
# Language Schemas
# ==========================================

class LanguageCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: str = Field(default="professional")

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip()
        return v


class LanguageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    proficiency: Optional[str] = None


class LanguageResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    name: str
    proficiency: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Career Preferences Schemas
# ==========================================

class CareerPreferencesUpdate(BaseModel):
    target_roles: Optional[List[str]] = None
    target_industries: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    employment_types: Optional[List[str]] = None
    availability_status: Optional[str] = None
    available_from: Optional[str] = None
    notice_period_days: Optional[int] = Field(None, ge=0)


class CareerPreferencesResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    target_roles: List[str]
    target_industries: List[str]
    preferred_locations: List[str]
    remote_preference: Optional[str] = None
    employment_types: List[str]
    availability_status: Optional[str] = None
    available_from: Optional[str] = None
    notice_period_days: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Root Candidate Profile Schemas
# ==========================================

class CandidateProfileCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    preferred_name: Optional[str] = Field(None, max_length=100)
    professional_headline: Optional[str] = Field(None, max_length=255)
    profile_photo: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    primary_title: Optional[str] = None
    secondary_titles: List[str] = Field(default_factory=list)
    career_level: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[float] = Field(None, ge=0)
    specializations: List[str] = Field(default_factory=list)
    base_summary: Optional[str] = None

    @field_validator("first_name", mode="before")
    @classmethod
    def validate_first_name(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("first_name cannot be empty.")
            return v_strip
        return v


class CandidateProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    preferred_name: Optional[str] = Field(None, max_length=100)
    professional_headline: Optional[str] = Field(None, max_length=255)
    profile_photo: Optional[str] = Field(None, max_length=500)
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    primary_title: Optional[str] = None
    secondary_titles: Optional[List[str]] = None
    career_level: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[float] = Field(None, ge=0)
    specializations: Optional[List[str]] = None
    base_summary: Optional[str] = None


class ProfileQualityBreakdown(BaseModel):
    score: int = Field(ge=0, le=100, description="Composite profile quality score (0-100)")
    completeness: int = Field(ge=0, le=100, description="Overall completeness percentage")
    evidence_coverage: int = Field(ge=0, le=100, description="Percentage of key claims backed by evidence")
    skill_validation: int = Field(ge=0, le=100, description="Percentage of skills linked to experiences/projects")
    experience_quality: int = Field(ge=0, le=100, description="Depth and metric quality of experience records")
    project_quality: int = Field(ge=0, le=100, description="Completeness of technical architecture and project details")
    achievement_quality: int = Field(ge=0, le=100, description="Verification and context of achievements")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations to improve profile quality")


class ProfileStrengthResponse(BaseModel):
    # Completion details (backward-compatible)
    completion_percentage: int
    sections_breakdown: Dict[str, bool]
    completed_sections_count: int
    total_sections_count: int
    suggestions: List[str]

    # Enhanced Phase 1.1 Quality breakdown
    score: int = 0
    completeness: int = 0
    evidence_coverage: int = 0
    skill_validation: int = 0
    experience_quality: int = 0
    project_quality: int = 0
    achievement_quality: int = 0
    recommendations: List[str] = Field(default_factory=list)
    quality: Optional[ProfileQualityBreakdown] = None


class CandidateProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    professional_headline: Optional[str] = None
    profile_photo: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    primary_title: Optional[str] = None
    secondary_titles: List[str] = Field(default_factory=list)
    career_level: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[float] = None
    specializations: List[str] = Field(default_factory=list)
    base_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Normalized child collections
    links: List[LinkResponse] = Field(default_factory=list)
    experiences: List[WorkExperienceResponse] = Field(default_factory=list)
    education: List[EducationResponse] = Field(default_factory=list)
    skills: List[SkillResponse] = Field(default_factory=list)
    projects: List[ProjectResponse] = Field(default_factory=list)
    certifications: List[CertificationResponse] = Field(default_factory=list)
    achievements: List[AchievementResponse] = Field(default_factory=list)
    languages: List[LanguageResponse] = Field(default_factory=list)
    career_preferences: Optional[CareerPreferencesResponse] = None
    evidence_items: List[EvidenceResponse] = Field(default_factory=list)

    # Strength calculation
    strength: Optional[ProfileStrengthResponse] = None
    quality: Optional[ProfileQualityBreakdown] = None

    model_config = ConfigDict(from_attributes=True)

