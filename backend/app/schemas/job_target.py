from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator


class JobTargetStatus(str, Enum):
    SAVED = "saved"
    ARCHIVED = "archived"


class JobRequirementCategory(str, Enum):
    SKILLS = "skills"
    TECHNOLOGIES = "technologies"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    RESPONSIBILITIES = "responsibilities"
    CONSTRAINTS = "constraints"
    KEYWORDS = "keywords"


class CandidateMatchStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIAL = "partial"
    UNVERIFIED = "unverified"
    MISSING = "missing"


class GapType(str, Enum):
    ABSENT_FROM_PROFILE = "absent_from_profile"
    UNVERIFIED_CLAIM = "unverified_claim"
    SKILL_GAP = "skill_gap"


class EvidenceTraceItem(BaseModel):
    """Traceable evidence item supporting a candidate match."""

    id: uuid.UUID
    title: str
    source: str
    source_type: str = "link"
    url: Optional[str] = None
    verification_status: str = "unverified"
    date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class JobRequirementItem(BaseModel):
    """
    Canonical requirement model as specified by the Job Intelligence Foundation:
    JobRequirementItem: { id, category, requirement, is_mandatory, candidate_match_status }
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    category: str = Field(..., description="Category e.g. 'skills', 'technologies', 'experience', 'education', 'certifications', 'responsibilities', 'constraints'")
    requirement: str = Field(..., min_length=1, description="Extracted requirement text")
    is_mandatory: bool = Field(default=True, description="True for mandatory/required, False for preferred/nice-to-have")
    candidate_match_status: str = Field(
        default=CandidateMatchStatus.MISSING.value,
        description="Match status: 'supported', 'partial', 'unverified', or 'missing'",
    )

    # Traceability and Explainability Extensions
    reasoning: Optional[str] = Field(None, description="Detailed explainable reasoning for the match status")
    matched_entity_type: Optional[str] = Field(None, description="Entity type: 'skill', 'experience', 'project', 'education', 'certification', 'achievement'")
    matched_entity_id: Optional[uuid.UUID] = Field(None, description="UUID of the matched profile entity")
    matched_entity_name: Optional[str] = Field(None, description="Name or title of the matched profile entity")
    evidence_ids: List[uuid.UUID] = Field(default_factory=list, description="IDs of supporting evidence records")
    evidence_items: List[EvidenceTraceItem] = Field(default_factory=list, description="Structured details of supporting evidence")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Match confidence score between 0.0 and 1.0")
    gap_type: Optional[str] = Field(None, description="Nature of the gap: 'absent_from_profile', 'unverified_claim', or 'skill_gap'")

    model_config = ConfigDict(from_attributes=True)


class KeywordSummary(BaseModel):
    """Aggregate metrics and keyword coverage statistics for a job target analysis."""

    total_requirements: int = 0
    mandatory_count: int = 0
    preferred_count: int = 0
    supported_count: int = 0
    partial_count: int = 0
    unverified_count: int = 0
    missing_count: int = 0
    coverage_percentage: float = 0.0
    mandatory_coverage_percentage: float = 0.0
    top_matched_keywords: List[str] = Field(default_factory=list)
    top_missing_keywords: List[str] = Field(default_factory=list)
    identified_gaps: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class JobAnalysisResult(BaseModel):
    """Structured extraction and evidence-grounded matching analysis result."""

    job_id: uuid.UUID
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    role_overview: Optional[str] = None
    seniority_level: Optional[str] = None
    employment_type: Optional[str] = None
    requirements: List[JobRequirementItem] = Field(default_factory=list)
    keyword_summary: KeywordSummary = Field(default_factory=KeywordSummary)

    model_config = ConfigDict(from_attributes=True)


class JobAnalysisResponse(BaseModel):
    """API response model for job analysis endpoint."""

    job_id: uuid.UUID
    job_title: str
    company_name: str
    analysis: JobAnalysisResult

    model_config = ConfigDict(from_attributes=True)


class JobExtractionRequest(BaseModel):
    """Ad-hoc extraction payload without saving."""

    job_description: str = Field(..., min_length=1, max_length=50000, description="Job description text")
    title: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)

    @field_validator("job_description", mode="before")
    @classmethod
    def validate_job_description(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Job description cannot be empty or blank whitespace.")
            return v_strip
        return v


class JobExtractionResult(BaseModel):
    """Result of structured requirement extraction."""

    role_overview: Optional[str] = None
    seniority_level: Optional[str] = None
    employment_type: Optional[str] = None
    requirements: List[JobRequirementItem] = Field(default_factory=list)
    extracted_keywords: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class JobTargetCreate(BaseModel):
    """Payload for creating a new job target opportunity."""

    title: str = Field(..., min_length=1, max_length=200, description="Job title / role name")
    company_name: str = Field(..., min_length=1, max_length=200, description="Company / employer name")
    location: Optional[str] = Field(None, max_length=200, description="Job location (e.g., 'San Francisco, CA (Hybrid)')")
    employment_type: Optional[str] = Field(None, max_length=50, description="Employment type (e.g., 'Full-time', 'Contract', 'Remote')")
    job_description: str = Field(..., min_length=1, max_length=50000, description="Full job description text")
    source_url: Optional[str] = Field(None, max_length=500, description="Job listing URL")
    user_notes: Optional[str] = Field(None, max_length=10000, description="Private candidate notes")
    status: JobTargetStatus = Field(default=JobTargetStatus.SAVED, description="Job lifecycle status")

    @field_validator("title", "company_name", mode="before")
    @classmethod
    def strip_required_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Field cannot be empty or blank whitespace.")
            return v_strip
        return v

    @field_validator("location", "employment_type", "user_notes", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            return v_strip if v_strip else None
        return v

    @field_validator("job_description", mode="before")
    @classmethod
    def validate_job_description(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Job description cannot be empty or blank whitespace.")
            return v_strip
        return v

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Source URL must start with http:// or https://")
            return v_strip
        return None


class JobTargetUpdate(BaseModel):
    """Payload for updating an existing job target opportunity."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    employment_type: Optional[str] = Field(None, max_length=50)
    job_description: Optional[str] = Field(None, min_length=1, max_length=50000)
    source_url: Optional[str] = Field(None, max_length=500)
    user_notes: Optional[str] = Field(None, max_length=10000)
    status: Optional[JobTargetStatus] = None

    @field_validator("title", "company_name", mode="before")
    @classmethod
    def strip_required_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Field cannot be empty or blank whitespace.")
            return v_strip
        return v

    @field_validator("location", "employment_type", "user_notes", mode="before")
    @classmethod
    def strip_optional_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            return v_strip if v_strip else None
        return v

    @field_validator("job_description", mode="before")
    @classmethod
    def validate_job_description(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_strip = v.strip()
            if not v_strip:
                raise ValueError("Job description cannot be empty or blank whitespace.")
            return v_strip
        return v

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v_strip = v.strip()
            if not (v_strip.startswith("http://") or v_strip.startswith("https://")):
                raise ValueError("Source URL must start with http:// or https://")
            return v_strip
        return None


class JobTargetResponse(BaseModel):
    """Response model representing a job target."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    company_name: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    job_description: str
    source_url: Optional[str] = None
    user_notes: Optional[str] = None
    status: JobTargetStatus
    analysis_result: Optional[JobAnalysisResult] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobTargetListResponse(BaseModel):
    """Paginated list response model for job targets."""

    items: List[JobTargetResponse]
    total: int
    limit: int
    offset: int
