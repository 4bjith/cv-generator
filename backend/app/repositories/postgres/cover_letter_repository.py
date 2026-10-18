import uuid
from typing import List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cover_letter import CoverLetter
from app.repositories.interfaces.cover_letter_repository import ICoverLetterRepository


class PostgresCoverLetterRepository(ICoverLetterRepository):
    """PostgreSQL / SQLAlchemy implementation of ICoverLetterRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, cover_letter: CoverLetter) -> CoverLetter:
        self.session.add(cover_letter)
        await self.session.flush()
        stmt = (
            select(CoverLetter)
            .where(CoverLetter.id == cover_letter.id)
            .options(
                selectinload(CoverLetter.job_target),
                selectinload(CoverLetter.cv_version),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(
        self,
        letter_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[CoverLetter]:
        if isinstance(letter_id, str):
            try:
                letter_id = uuid.UUID(letter_id)
            except ValueError:
                return None
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        stmt = (
            select(CoverLetter)
            .where(
                CoverLetter.id == letter_id,
                CoverLetter.user_id == user_id,
            )
            .options(
                selectinload(CoverLetter.job_target),
                selectinload(CoverLetter.cv_version),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        job_target_id: Optional[Union[uuid.UUID, str]] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[CoverLetter], int]:
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return [], 0

        filters = [CoverLetter.user_id == user_id]

        if status:
            filters.append(CoverLetter.status == status)

        if job_target_id:
            if isinstance(job_target_id, str):
                try:
                    job_target_id = uuid.UUID(job_target_id)
                except ValueError:
                    return [], 0
            filters.append(CoverLetter.job_target_id == job_target_id)

        if search:
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    CoverLetter.name.ilike(search_pattern),
                    CoverLetter.recipient_company.ilike(search_pattern),
                    CoverLetter.recipient_name.ilike(search_pattern),
                )
            )

        # Count total
        count_stmt = select(func.count(CoverLetter.id)).where(*filters)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data query
        stmt = (
            select(CoverLetter)
            .where(*filters)
            .options(
                selectinload(CoverLetter.job_target),
                selectinload(CoverLetter.cv_version),
            )
            .order_by(CoverLetter.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def update(self, cover_letter: CoverLetter) -> CoverLetter:
        self.session.add(cover_letter)
        await self.session.flush()
        stmt = (
            select(CoverLetter)
            .where(CoverLetter.id == cover_letter.id)
            .options(
                selectinload(CoverLetter.job_target),
                selectinload(CoverLetter.cv_version),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, cover_letter: CoverLetter) -> None:
        await self.session.delete(cover_letter)
        await self.session.flush()
