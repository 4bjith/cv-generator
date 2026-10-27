import asyncio
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from fastapi import Depends

from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.base import utc_now
from app.models.user import User
from app.repositories.interfaces.auth_session_repository import IAuthSessionRepository
from app.repositories.interfaces.user_repository import IUserRepository
from app.repositories.user_repository import get_auth_session_repository, get_user_repository
from app.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse, UserResponse

settings = get_settings()


def hash_token(token: str) -> str:
    """Compute a SHA-256 fingerprint hash of a raw token for secure database indexing and lookup."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    """Business logic for user registration, authentication, token rotation, and persisted session revocation."""

    def __init__(
        self,
        user_repo: IUserRepository,
        session_repo: IAuthSessionRepository,
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo

    def _to_user_response(self, user: User) -> UserResponse:
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if isinstance(user.created_at, datetime) else str(user.created_at),
        )

    async def _issue_and_persist_tokens(
        self,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        user_id_str = str(user.id)
        access_token = create_access_token(subject=user.email, user_id=user_id_str)
        refresh_token = create_refresh_token(subject=user.email, user_id=user_id_str)
        expires_in = settings.access_token_expire_minutes * 60

        # Compute expiration time for the database record
        expires_at = utc_now() + timedelta(days=settings.refresh_token_expire_days)
        token_hash = hash_token(refresh_token)

        # Persist session to PostgreSQL
        await self.session_repo.create_session(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=self._to_user_response(user),
        )

    async def register(
        self,
        request: RegisterRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """Register a new candidate account in PostgreSQL and create an initial auth session."""
        normalized_email = request.email.strip().lower()
        existing_user = await self.user_repo.get_by_email(normalized_email)
        if existing_user:
            raise ConflictError(
                message="An account with this email address already exists.",
                code="EMAIL_ALREADY_EXISTS",
            )

        hashed = await asyncio.to_thread(hash_password, request.password)
        user = await self.user_repo.create(
            email=normalized_email,
            password_hash=hashed,
            name=request.full_name,
        )

        return await self._issue_and_persist_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def login(
        self,
        request: LoginRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """Authenticate candidate credentials, update last login, and issue an auth session."""
        normalized_email = request.email.strip().lower()
        user = await self.user_repo.get_by_email(normalized_email)
        if not user:
            raise UnauthorizedError(
                message="Invalid email address or password.",
                code="INVALID_CREDENTIALS",
            )

        is_valid_password = await asyncio.to_thread(verify_password, request.password, user.password_hash)
        if not is_valid_password:
            raise UnauthorizedError(
                message="Invalid email address or password.",
                code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise ForbiddenError(
                message="This user account is deactivated.",
                code="ACCOUNT_DEACTIVATED",
            )

        # Update last_login_at timestamp
        await self.user_repo.update_last_login(user.id, utc_now())

        return await self._issue_and_persist_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def refresh_tokens(
        self,
        request: RefreshTokenRequest,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> TokenResponse:
        """Verify refresh token signature and database persistence, rotate the session, and issue a new token pair."""
        payload = decode_token(request.refresh_token, expected_type="refresh")
        user_id_str = payload.get("uid")
        if not user_id_str:
            raise UnauthorizedError("Invalid refresh token claims.", code="INVALID_TOKEN_CLAIMS")

        token_hash = hash_token(request.refresh_token)

        # Check database for active session
        session = await self.session_repo.get_active_session_by_token_hash(token_hash)
        if not session:
            # Check if this token was previously revoked (reuse detection hint)
            all_session = await self.session_repo.get_session_by_token_hash(token_hash)
            if all_session and all_session.revoked_at is not None:
                raise UnauthorizedError(
                    "This refresh session has already been revoked. Please log in again.",
                    code="REVOKED_REFRESH_TOKEN",
                )
            raise UnauthorizedError(
                "Invalid or expired refresh token session.",
                code="INVALID_REFRESH_SESSION",
            )

        user = await self.user_repo.get_by_id(user_id_str)
        if not user:
            raise UnauthorizedError("User account associated with token not found.", code="USER_NOT_FOUND")

        if not user.is_active:
            raise ForbiddenError("This user account is deactivated.", code="ACCOUNT_DEACTIVATED")

        # 1. Rotate: Revoke the old session
        await self.session_repo.revoke_session(session.id)

        # 2. Issue fresh token pair and persist new session
        return await self._issue_and_persist_tokens(user, user_agent=user_agent, ip_address=ip_address)

    async def get_user_by_id(self, user_id: Union[uuid.UUID, str]) -> UserResponse:
        """Retrieve user identity by user UUID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.", code="USER_NOT_FOUND")
        return self._to_user_response(user)

    async def logout(
        self,
        user_id: Union[uuid.UUID, str],
        refresh_token: Optional[str] = None,
    ) -> None:
        """Revoke active session(s) in PostgreSQL."""
        if refresh_token:
            token_hash = hash_token(refresh_token)
            session = await self.session_repo.get_session_by_token_hash(token_hash)
            if session:
                await self.session_repo.revoke_session(session.id)
                return

        # If no specific refresh token is provided, revoke all active sessions for this user
        await self.session_repo.revoke_all_user_sessions(user_id)


def get_auth_service(
    user_repo: IUserRepository = Depends(get_user_repository),
    session_repo: IAuthSessionRepository = Depends(get_auth_session_repository),
) -> AuthService:
    """FastAPI dependency provider for AuthService with injected PostgreSQL repositories."""
    return AuthService(user_repo=user_repo, session_repo=session_repo)
