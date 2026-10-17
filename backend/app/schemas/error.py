from typing import Any, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed validation or field-level error item."""

    field: Optional[str] = Field(None, description="The dotted field path that failed validation")
    message: str = Field(..., description="Human-readable error explanation for this field")
    type: Optional[str] = Field(None, description="Error type identifier")


class ErrorBody(BaseModel):
    """Standard error payload structure."""

    code: str = Field(..., description="Application error code (e.g. VALIDATION_ERROR, NOT_FOUND)")
    message: str = Field(..., description="High-level description of what went wrong")
    request_id: Optional[str] = Field(None, description="Traceable correlation ID for the request")
    details: Optional[list[Any]] = Field(None, description="Optional array of detailed errors or field issues")


class ErrorResponse(BaseModel):
    """Envelope model for all non-2xx API error responses."""

    error: ErrorBody
