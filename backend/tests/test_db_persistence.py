import uuid
from datetime import timedelta
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import utc_now
from app.models.auth_session import AuthSession
from app.models.user import User
from app.repositories.postgres.auth_session_repository import PostgresAuthSessionRepository
from app.repositories.postgres.user_repository import PostgresUserRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession) -> None:
    """Verify PostgresUserRepository persists and queries User entities correctly."""
    repo = PostgresUserRepository(db_session)

    user = await repo.create(
        email="Direct.Test@Example.Com",
        password_hash="hashed_secret_123",
        name="Direct Tester",
    )
    await db_session.commit()

    assert user.id is not None
    assert user.email == "direct.test@example.com"  # Normalized to lowercase
    assert user.name == "Direct Tester"
    assert user.is_active is True
    assert user.created_at is not None

    # Retrieve by ID
    found = await repo.get_by_id(user.id)
    assert found is not None
    assert found.email == "direct.test@example.com"

    # Retrieve by string ID
    found_str = await repo.get_by_id(str(user.id))
    assert found_str is not None
    assert found_str.id == user.id

    # Retrieve by Email
    found_email = await repo.get_by_email("DIRECT.TEST@EXAMPLE.COM")
    assert found_email is not None
    assert found_email.id == user.id

    # Update last login
    now = utc_now()
    await repo.update_last_login(user.id, now)
    await db_session.commit()

    refreshed = await repo.get_by_id(user.id)
    assert refreshed.last_login_at is not None


@pytest.mark.asyncio
async def test_user_email_unique_constraint(db_session: AsyncSession) -> None:
    """Verify unique constraint prevents duplicate emails at database level."""
    repo = PostgresUserRepository(db_session)

    await repo.create(
        email="unique.check@example.com",
        password_hash="hash1",
        name="User 1",
    )
    await db_session.commit()

    with pytest.raises(IntegrityError):
        # Attempt to insert identical email
        dupe_user = User(
            id=uuid.uuid4(),
            email="unique.check@example.com",
            password_hash="hash2",
            name="User 2",
        )
        db_session.add(dupe_user)
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_auth_session_repository_lifecycle(db_session: AsyncSession) -> None:
    """Verify PostgresAuthSessionRepository creates, queries, and revokes sessions."""
    user_repo = PostgresUserRepository(db_session)
    session_repo = PostgresAuthSessionRepository(db_session)

    user = await user_repo.create(
        email="session.test@example.com",
        password_hash="some_hash",
        name="Session Tester",
    )
    await db_session.commit()

    expires = utc_now() + timedelta(days=7)
    token_hash = "sha256_mock_hash_value_123456"

    # Create session
    session = await session_repo.create_session(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires,
        user_agent="Mozilla/5.0 TestAgent",
        ip_address="192.168.1.100",
    )
    await db_session.commit()

    assert session.id is not None
    assert session.user_id == user.id
    assert session.refresh_token_hash == token_hash
    assert session.revoked_at is None
    assert session.is_active is True

    # Look up active session
    active = await session_repo.get_active_session_by_token_hash(token_hash)
    assert active is not None
    assert active.id == session.id

    # Revoke session
    await session_repo.revoke_session(session.id)
    await db_session.commit()

    # Verify no longer returned by get_active_session_by_token_hash
    active_after = await session_repo.get_active_session_by_token_hash(token_hash)
    assert active_after is None

    # Verify still exists in database as revoked
    any_session = await session_repo.get_session_by_token_hash(token_hash)
    assert any_session is not None
    assert any_session.revoked_at is not None


@pytest.mark.asyncio
async def test_cascade_delete_user_sessions(db_session: AsyncSession) -> None:
    """Verify deleting a User record cascades and removes associated AuthSession records."""
    user_repo = PostgresUserRepository(db_session)
    session_repo = PostgresAuthSessionRepository(db_session)

    user = await user_repo.create(
        email="cascade.test@example.com",
        password_hash="hash",
        name="Cascade Tester",
    )
    await db_session.commit()

    session = await session_repo.create_session(
        user_id=user.id,
        token_hash="cascade_token_hash",
        expires_at=utc_now() + timedelta(days=1),
    )
    await db_session.commit()

    # Delete the user
    await db_session.delete(user)
    await db_session.commit()

    # Confirm session was deleted
    result = await db_session.execute(
        select(AuthSession).where(AuthSession.id == session.id)
    )
    assert result.scalars().first() is None
