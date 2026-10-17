from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr = Field(..., description="Unique email address", examples=["candidate@example.com"])
    password: str = Field(..., min_length=8, max_length=128, description="Password (at least 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of the user", examples=["Aarav Mehta"])


class LoginRequest(BaseModel):
    """User authentication payload."""

    email: EmailStr = Field(..., description="Registered email address", examples=["candidate@example.com"])
    password: str = Field(..., min_length=1, max_length=128, description="Account password")


class RefreshTokenRequest(BaseModel):
    """Refresh token payload for extending access."""

    refresh_token: str = Field(..., description="Valid JWT refresh token")


class UserResponse(BaseModel):
    """Public user identity model without sensitive credential fields."""

    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's display name")
    is_active: bool = Field(True, description="Account active status")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")


class TokenResponse(BaseModel):
    """Token response containing signed access and refresh tokens."""

    access_token: str = Field(..., description="Short-lived JWT access token")
    refresh_token: str = Field(..., description="Longer-lived JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry duration in seconds")
    user: UserResponse = Field(..., description="Authenticated user profile")
