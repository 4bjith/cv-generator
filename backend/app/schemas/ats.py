from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cv import CVContentSnapshot


class ATSCheckSeverity(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    REVIEW = "review"
    INFO = "info"


class ATSCheckCategory(str, Enum):
    CONTACT_INFO = "contact_info"
    HEADINGS = "headings"
    DATES = "dates"
    TEMPLATE_LAYOUT = "template_layout"
    SYMBOLS_AND_FORMATTING = "symbols_and_formatting"
    KEYWORD_DENSITY = "keyword_density"
    CONTENT_QUALITY = "content_quality"


class ATSCheckItem(BaseModel):
    """Specific check result evaluating structure, formatting, or parsing friction."""

    id: str = Field(..., description="Unique check identifier")
    label: str = Field(..., description="Human-readable check title")
    category: ATSCheckCategory = Field(..., description="Classification category")
    status: ATSCheckSeverity = Field(..., description="Check status: pass, warning, review, info")
    detail: str = Field(..., description="Detailed explanation of the findings")
    recommendation: Optional[str] = Field(None, description="Actionable recommendation if issue detected")

    model_config = ConfigDict(from_attributes=True)


class ATSComponentScore(BaseModel):
    """Component scoring breakdown with clear explanation for points awarded or deducted."""

    name: str = Field(..., description="Component label")
    score: float = Field(..., ge=0, description="Points awarded")
    max_score: float = Field(..., gt=0, description="Maximum possible points for component")
    weight_percentage: float = Field(..., ge=0, le=100, description="Percentage weight in overall score")
    explanation: str = Field(..., description="Human-readable explanation of awarded points")
    deductions: List[str] = Field(default_factory=list, description="List of specific deductions applied")

    model_config = ConfigDict(from_attributes=True)


class KeywordOccurrenceItem(BaseModel):
    """Frequency, presence, and density metric for a specific keyword in the CV."""

    keyword: str = Field(..., description="Target keyword or phrase")
    count: int = Field(default=0, ge=0, description="Number of occurrences in CV")
    density_percentage: float = Field(default=0.0, ge=0.0, description="Percentage of total word count")
    is_mandatory: bool = Field(default=False, description="True if required by target job")
    is_present: bool = Field(default=False, description="True if found in CV")
    is_overused: bool = Field(default=False, description="True if exceeds safe density threshold (>3.5%)")
    locations_found: List[str] = Field(default_factory=list, description="CV sections where keyword was detected")

    model_config = ConfigDict(from_attributes=True)


class GroundedKeywordSuggestion(BaseModel):
    """Actionable keyword suggestion distinguished by candidate profile evidence."""

    id: str = Field(..., description="Unique suggestion identifier")
    keyword: str = Field(..., description="Suggested keyword")
    is_mandatory: bool = Field(default=False, description="Whether this is a required qualification")
    is_grounded_in_profile: bool = Field(..., description="True if candidate profile has factual evidence")
    grounding_evidence: Optional[str] = Field(None, description="Reference to candidate profile evidence")
    suggested_action: str = Field(..., description="Recommended placement in CV")
    target_section: str = Field(default="skills", description="Target section in CV snapshot")
    sample_text: Optional[str] = Field(None, description="Example text or skill addition")
    status: str = Field(default="pending", description="pending, accepted, rejected")
    warning: Optional[str] = Field(None, description="Warning if unsupported: never fabricate experience")

    model_config = ConfigDict(from_attributes=True)


class ATSAnalysisRequest(BaseModel):
    """Request payload to analyze a CV version."""

    cv_version_id: uuid.UUID = Field(..., description="CVVersion UUID to analyze")
    job_id: Optional[uuid.UUID] = Field(None, description="Optional target JobTarget UUID for targeted match")


class ATSAnalysisResponse(BaseModel):
    """Comprehensive ATS analysis report with explainable scoring and parsing audit."""

    id: str = Field(..., description="Report identifier")
    cv_version_id: uuid.UUID
    cv_version_name: str
    job_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    overall_score: int = Field(..., ge=0, le=100, description="Composite score (0-100)")
    scoring_mode: str = Field(default="job_targeted", description="'job_targeted' or 'general_baseline'")
    components: List[ATSComponentScore] = Field(default_factory=list)
    keyword_coverage_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    total_words: int = Field(default=0, ge=0)
    checks: List[ATSCheckItem] = Field(default_factory=list)
    keywords: List[KeywordOccurrenceItem] = Field(default_factory=list)
    suggestions: List[GroundedKeywordSuggestion] = Field(default_factory=list)
    disclaimer: str = Field(
        default="Heuristic estimate only: No algorithm guarantees ATS compatibility or job interview selection. ATS systems parse and rank according to individual recruiter filters and employer criteria.",
        description="Mandatory disclaimer distinguishing heuristic estimation from guarantees",
    )
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class ApplyATSSuggestionsRequest(BaseModel):
    """Apply accepted keyword optimizations to create a new CVVersion snapshot."""

    cv_version_id: uuid.UUID = Field(..., description="Base CVVersion to duplicate and optimize")
    accepted_suggestion_ids: List[str] = Field(..., min_length=1, description="List of suggestion IDs to apply")
    job_id: Optional[uuid.UUID] = Field(None, description="Optional target JobTarget UUID")
    new_version_name: Optional[str] = Field(None, description="Optional custom name for new version")


class ApplyATSSuggestionsResponse(BaseModel):
    """Result of applying keyword optimizations, confirming new independent version."""

    original_version_id: uuid.UUID
    new_version_id: uuid.UUID
    new_version_name: str
    applied_suggestions_count: int
    content_snapshot: CVContentSnapshot
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
