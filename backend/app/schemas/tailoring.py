from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cv import CVContentSnapshot, CVVersionResponse


class CVTailorRequest(BaseModel):
    """Request payload to initiate evidence-grounded AI CV tailoring."""

    template: Optional[str] = Field("modern", description="Target CV presentation template")
    tone: Optional[str] = Field("professional", description="Tone of voice (e.g. professional, executive, technical)")
    target_role: Optional[str] = Field(None, description="Explicit role title override if desired")
    focus_areas: List[str] = Field(default_factory=list, description="Specific skills or experiences to emphasize")
    custom_instructions: Optional[str] = Field(None, max_length=1000, description="Optional candidate instructions")
    include_clarifications: bool = Field(default=True, description="Whether to include confirmed clarification answers")


class TailoredWorkExperienceItem(BaseModel):
    """Structured tailored experience with factual, grounded highlights."""

    id: Optional[uuid.UUID] = None
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    tailored_highlights: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    relevance_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StructuredTailoringOutput(BaseModel):
    """Structured LLM output schema for AI provider generation."""

    tailored_summary: str = Field(..., description="Targeted professional summary grounded entirely in candidate facts")
    target_role: str = Field(..., description="Target role title")
    relevant_skills: List[str] = Field(default_factory=list, description="Skills strictly from candidate profile ordered by job relevance")
    tailored_highlights: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of company_name or experience_id to tailored bullet points highlighting job-relevant facts"
    )
    change_summary: List[str] = Field(
        default_factory=list,
        description="Explanations of tailoring decisions made (e.g. summary emphasis, keyword ordering)"
    )
    unresolved_gaps: List[str] = Field(
        default_factory=list,
        description="Requirements from job description that could NOT be fulfilled because candidate lacks evidence"
    )

    model_config = ConfigDict(from_attributes=True)


class CVTailoringResponse(BaseModel):
    """Complete response returned after tailored CV generation."""

    cv_version_id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    company_name: str
    version_name: str
    status: str
    content_snapshot: CVContentSnapshot
    change_summary: List[str] = Field(default_factory=list)
    unresolved_gaps: List[str] = Field(default_factory=list)
    quality_score: float = Field(default=95.0, ge=0.0, le=100.0)
    unsupported_claims_prevented: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
