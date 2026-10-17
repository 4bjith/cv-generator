from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import UnauthorizedError
from app.core.logging import user_id_ctx
from app.core.security import decode_token
from app.schemas.auth import UserResponse
from app.services.auth_service import AuthService, get_auth_service

# Reusable Bearer scheme for OpenAPI documentation
bearer_scheme = HTTPBearer(
    auto_error=False,
    description="JWT Bearer token. Format: `Bearer <access_token>`",
)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Dependency that extracts, decodes, and validates the JWT Bearer token, returning the current user."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedError(
            message="Authentication credentials were not provided in the Authorization header.",
            code="AUTHENTICATION_REQUIRED",
        )

    token = credentials.credentials
    payload = decode_token(token, expected_type="access")

    user_id = payload.get("uid")
    if not user_id:
        raise UnauthorizedError(
            message="Invalid token payload: missing user identifier.",
            code="INVALID_TOKEN_PAYLOAD",
        )

    # Set user_id in logging context variable for traceability
    user_id_ctx.set(user_id)

    user = await auth_service.get_user_by_id(user_id)
    if not user.is_active:
        raise UnauthorizedError(
            message="User account has been deactivated.",
            code="ACCOUNT_DEACTIVATED",
        )

    return user
