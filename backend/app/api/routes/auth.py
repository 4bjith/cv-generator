import time
from collections import defaultdict
from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.exceptions import RateLimitError
from app.core.middleware import get_client_ip
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import GenericMessageResponse
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter for brute-force protection."""

    def __init__(self, limit: int = 15, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        timestamps = [t for t in self._requests[key] if t > window_start]
        if len(timestamps) >= self.limit:
            raise RateLimitError(
                message=f"Too many authentication attempts. Please try again in {self.window_seconds} seconds.",
                code="AUTH_RATE_LIMIT_EXCEEDED",
            )
        timestamps.append(now)
        self._requests[key] = timestamps


auth_rate_limiter = SlidingWindowRateLimiter(limit=15, window_seconds=60)


def _extract_client_info(request: Request) -> tuple[str, str]:
    user_agent = request.headers.get("user-agent") or "unknown"
    client_ip = get_client_ip(request)
    return user_agent, client_ip


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new candidate account in PostgreSQL and return signed access and refresh tokens.",
)
async def register(
    request_body: RegisterRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Register a new candidate with email, password, and full name."""
    user_agent, client_ip = _extract_client_info(http_request)
    if settings.app_env != "test":
        auth_rate_limiter.check(client_ip)

    return await auth_service.register(
        request_body,
        user_agent=user_agent,
        ip_address=client_ip,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate credentials and issue a new JWT access and refresh token pair.",
)
async def login(
    request_body: LoginRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate with registered email and password."""
    user_agent, client_ip = _extract_client_info(http_request)
    if settings.app_env != "test":
        auth_rate_limiter.check(client_ip)

    return await auth_service.login(
        request_body,
        user_agent=user_agent,
        ip_address=client_ip,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Retrieve the authenticated user's profile details.",
)
async def get_me(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Return profile data for the authenticated token bearer."""
    return current_user


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Exchange a valid refresh token for a newly issued access token and refresh token pair with rotation.",
)
async def refresh_token(
    request_body: RefreshTokenRequest,
    http_request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Refresh expired access credentials using a long-lived refresh token."""
    user_agent, client_ip = _extract_client_info(http_request)
    return await auth_service.refresh_tokens(
        request_body,
        user_agent=user_agent,
        ip_address=client_ip,
    )


@router.post(
    "/logout",
    response_model=GenericMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Log out the authenticated user session and revoke database refresh sessions.",
)
async def logout(
    current_user: UserResponse = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> GenericMessageResponse:
    """Perform logout for the authenticated user."""
    await auth_service.logout(current_user.id)
    return GenericMessageResponse(message="Successfully logged out.")
