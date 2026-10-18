from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ResponseMeta(BaseModel):
    """Metadata envelope for responses."""

    request_id: Optional[str] = Field(None, description="Request ID associated with the operation")
    timestamp: Optional[str] = Field(None, description="UTC timestamp of response generation")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success wrapper for endpoints utilizing structured response envelopes."""

    data: DataT
    meta: Optional[ResponseMeta] = None


class GenericMessageResponse(BaseModel):
    """Simple operational message response."""

    message: str = Field(..., description="Status or result message")
    request_id: Optional[str] = Field(None, description="Request correlation ID")


class HealthLiveResponse(BaseModel):
    """Response model for liveness probe."""

    status: str = Field("ok", description="Process liveness status")


class HealthReadyResponse(BaseModel):
    """Response model for readiness probe with dependency health checks."""

    status: str = Field("ok", description="Overall readiness status ('ok' or 'degraded')")
    checks: dict[str, str] = Field(
        default_factory=lambda: {"application": "ok"},
        description="Dictionary of individual component health statuses",
    )
    ai: Optional[dict[str, Any]] = Field(
        default=None,
        description="Safe, non-sensitive AI provider configuration metadata",
    )
