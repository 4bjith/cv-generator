from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ClarificationQuestionStatus(str, Enum):
    UNANSWERED = "unanswered"
    ANSWERED = "answered"
    SKIPPED = "skipped"


class ClarificationQuestionItem(BaseModel):
    """Specific, prioritized clarification question targeting an unverified or missing requirement."""

    id: str = Field(..., description="Unique question identifier")
    job_id: uuid.UUID = Field(..., description="Target job UUID")
    requirement_id: Optional[uuid.UUID] = Field(None, description="Matched JobRequirementItem ID")
    requirement_text: str = Field(..., description="Target job requirement statement")
    is_mandatory: bool = Field(default=True, description="True for mandatory/must-have requirement")
    category: str = Field(default="skills", description="Requirement category (skills, technologies, experience, etc.)")
    gap_type: Optional[str] = Field(None, description="Nature of the gap (absent_from_profile, unverified_claim, skill_gap)")
    question: str = Field(..., description="Targeted, actionable question for candidate")
    context: str = Field(..., description="Reasoning and context explaining why clarification is requested")
    status: ClarificationQuestionStatus = Field(default=ClarificationQuestionStatus.UNANSWERED)
    answer: Optional[str] = Field(None, description="Candidate-provided answer text")
    answered_at: Optional[datetime] = None
    priority: int = Field(default=1, description="Priority ranking (1 = highest / mandatory, 2 = preferred)")
    suggested_options: List[str] = Field(default_factory=list, description="Helpful prompts or suggestions")
    save_to_profile: bool = Field(default=False, description="Candidate consent to persist answer into profile")
    provenance: str = Field(default="candidate_clarification", description="Data provenance origin")
    verification_status: str = Field(default="unverified", description="Candidate-confirmed claims remain unverified until external proof")

    model_config = ConfigDict(from_attributes=True)


class ClarificationSessionResponse(BaseModel):
    """Resumable clarification session state for a specific job target."""

    job_id: uuid.UUID
    job_title: str
    company_name: str
    total_questions: int = 0
    answered_count: int = 0
    skipped_count: int = 0
    unanswered_count: int = 0
    is_completed: bool = False
    questions: List[ClarificationQuestionItem] = Field(default_factory=list)
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClarificationAnswerRequest(BaseModel):
    """Candidate answer submission for a single clarification question."""

    answer: str = Field(..., min_length=1, max_length=3000, description="Candidate response text")
    save_to_profile: bool = Field(default=False, description="Whether to also add this confirmed answer to CandidateProfile")


class ClarificationBulkAnswerRequest(BaseModel):
    """Bulk update of multiple clarification answers."""

    answers: Dict[str, str] = Field(..., description="Mapping of question_id to answer string")
    save_to_profile: bool = Field(default=False)


class ClarificationPromoteRequest(BaseModel):
    """Promote confirmed clarification claim to Candidate Knowledge Base with verified provenance."""

    category: str = Field(default="skills", description="Target profile domain (skills, experience, projects)")
    skill_proficiency: Optional[str] = Field("intermediate", description="Proficiency level if promoting as skill")
