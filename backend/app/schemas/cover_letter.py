import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CoverLetterTone(str, Enum):
    PROFESSIONAL = "professional"
    CONCISE = "concise"
    TECHNICAL = "technical"
    FORMAL = "formal"


class CoverLetterLength(str, Enum):
    SHORT = "short"        # ~200-250 words
    STANDARD = "standard"  # ~300-400 words
    DETAILED = "detailed"  # ~450-600 words


class CoverLetterStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    ARCHIVED = "archived"


class FactualClaimItem(BaseModel):
    """Factual evidence claim cited within the cover letter body."""

    claim_text: str = Field(..., description="The factual statement or achievement in the letter.")
    entity_type: str = Field(
        ...,
        description="Type of candidate evidence (e.g. experience, project, skill, education, clarification).",
    )
    entity_id: Optional[str] = Field(None, description="Identifier of the referenced candidate knowledge base record.")
    verification_status: str = Field(
        default="verified",
        description="Verification state of the source claim (e.g. verified, unverified).",
    )


class StructuredCoverLetterOutput(BaseModel):
    """Structured schema returned by AIProvider for cover letter generation."""

    salutation: str = Field(default="Dear Hiring Manager,", description="Formal greeting to recipient.")
    opening: str = Field(..., description="Engaging opening identifying role, target company, and alignment hook.")
    body_paragraphs: List[str] = Field(
        ...,
        description="Body paragraphs demonstrating relevant accomplishments and evidence.",
    )
    closing: str = Field(..., description="Professional call-to-action and closing expression of interest.")
    sign_off: str = Field(default="Sincerely,", description="Formal sign-off phrase.")
    factual_claims: List[FactualClaimItem] = Field(
        default_factory=list,
        description="Candidate evidence items explicitly referenced in the letter.",
    )
    unresolved_gaps: List[str] = Field(
        default_factory=list,
        description="Target job requirements where candidate evidence was absent and thus unasserted.",
    )
    change_summary: Optional[str] = Field(
        default=None,
        description="Explanation of modifications made if regenerating an existing letter.",
    )


class GenerateCoverLetterRequest(BaseModel):
    """Request payload to generate a new evidence-grounded cover letter."""

    job_id: uuid.UUID = Field(..., description="Target JobTarget ID.")
    cv_version_id: Optional[uuid.UUID] = Field(None, description="Optional CVVersion ID for additional context.")
    tone: CoverLetterTone = Field(default=CoverLetterTone.PROFESSIONAL, description="Writing style/tone.")
    length_option: CoverLetterLength = Field(default=CoverLetterLength.STANDARD, description="Target document length.")
    additional_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional instructions from candidate (e.g. highlight specific project, mention relocation).",
    )
    recipient_name: Optional[str] = Field(None, max_length=200, description="Name of hiring manager or recruiter.")
    recipient_title: Optional[str] = Field(None, max_length=200, description="Title of recipient.")
    recipient_company: Optional[str] = Field(None, max_length=200, description="Company name if overriding.")
    recipient_address: Optional[str] = Field(None, max_length=300, description="Company street address / location.")
    name: Optional[str] = Field(None, max_length=200, description="Custom title for this cover letter version.")


class RegenerateCoverLetterRequest(BaseModel):
    """Request to regenerate an existing cover letter with adjusted parameters or instructions."""

    tone: Optional[CoverLetterTone] = Field(None, description="Updated tone/style.")
    length_option: Optional[CoverLetterLength] = Field(None, description="Updated length option.")
    additional_instructions: Optional[str] = Field(
        None,
        max_length=2000,
        description="New or revised instructions for the regeneration.",
    )
    preserve_as_new_version: bool = Field(
        default=True,
        description="If True, creates a new independent CoverLetter version; if False, updates current draft.",
    )
    new_name: Optional[str] = Field(None, max_length=200, description="Name for newly created version if preserved.")


class UpdateCoverLetterRequest(BaseModel):
    """Editable fields for a cover letter artifact."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[CoverLetterStatus] = None
    tone: Optional[CoverLetterTone] = None
    length_option: Optional[CoverLetterLength] = None
    recipient_name: Optional[str] = Field(None, max_length=200)
    recipient_title: Optional[str] = Field(None, max_length=200)
    recipient_company: Optional[str] = Field(None, max_length=200)
    recipient_address: Optional[str] = Field(None, max_length=300)
    salutation: Optional[str] = Field(None, max_length=200)
    opening: Optional[str] = None
    body_paragraphs: Optional[List[str]] = None
    closing: Optional[str] = None
    sign_off: Optional[str] = Field(None, max_length=200)
    sender_name: Optional[str] = Field(None, max_length=200)
    sender_contact: Optional[str] = Field(None, max_length=300)
    full_content: Optional[str] = None


class CoverLetterSummary(BaseModel):
    """Concise representation for cover letter library listing."""

    id: uuid.UUID
    name: str
    status: CoverLetterStatus
    tone: CoverLetterTone
    length_option: CoverLetterLength
    job_target_id: Optional[uuid.UUID] = None
    job_target_title: Optional[str] = None
    job_target_company: Optional[str] = None
    cv_version_id: Optional[uuid.UUID] = None
    cv_version_name: Optional[str] = None
    word_count: int
    created_at: datetime
    updated_at: datetime


class CoverLetterResponse(BaseModel):
    """Complete detail response for a cover letter."""

    id: uuid.UUID
    user_id: uuid.UUID
    job_target_id: Optional[uuid.UUID] = None
    job_target_title: Optional[str] = None
    job_target_company: Optional[str] = None
    cv_version_id: Optional[uuid.UUID] = None
    cv_version_name: Optional[str] = None
    name: str
    status: CoverLetterStatus
    tone: CoverLetterTone
    length_option: CoverLetterLength
    recipient_name: Optional[str] = None
    recipient_title: Optional[str] = None
    recipient_company: Optional[str] = None
    recipient_address: Optional[str] = None
    salutation: str
    opening: str
    body_paragraphs: List[str]
    closing: str
    sign_off: str
    sender_name: str
    sender_contact: Optional[str] = None
    full_content: str
    word_count: int
    factual_claims: List[FactualClaimItem]
    unresolved_gaps: List[str]
    change_summary: Optional[str] = None
    generation_parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
