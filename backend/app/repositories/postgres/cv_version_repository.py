import uuid
from typing import List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cv_version import CVVersion
from app.repositories.interfaces.cv_version_repository import ICVVersionRepository


class PostgresCVVersionRepository(ICVVersionRepository):
    """PostgreSQL / SQLAlchemy implementation of ICVVersionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, cv_version: CVVersion) -> CVVersion:
        self.session.add(cv_version)
        await self.session.flush()
        # Refresh with job_target relationship loaded
        stmt = (
            select(CVVersion)
            .where(CVVersion.id == cv_version.id)
            .options(selectinload(CVVersion.job_target))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_by_id(
        self,
        version_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[CVVersion]:
        if isinstance(version_id, str):
            try:
                version_id = uuid.UUID(version_id)
            except ValueError:
                return None
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        stmt = (
            select(CVVersion)
            .where(
                CVVersion.id == version_id,
                CVVersion.user_id == user_id,
            )
            .options(selectinload(CVVersion.job_target))
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
    ) -> Tuple[List[CVVersion], int]:
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return [], 0

        filters = [CVVersion.user_id == user_id]

        if status:
            filters.append(CVVersion.status == status)

        if job_target_id:
            if isinstance(job_target_id, str):
                try:
                    job_target_id = uuid.UUID(job_target_id)
                except ValueError:
                    return [], 0
            filters.append(CVVersion.job_target_id == job_target_id)

        if search:
            search_pattern = f"%{search.strip()}%"
            filters.append(CVVersion.name.ilike(search_pattern))

        # Count total matching records
        count_stmt = select(func.count(CVVersion.id)).where(*filters)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data query
        stmt = (
            select(CVVersion)
            .where(*filters)
            .options(selectinload(CVVersion.job_target))
            .order_by(CVVersion.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def update(self, cv_version: CVVersion) -> CVVersion:
        self.session.add(cv_version)
        await self.session.flush()
        stmt = (
            select(CVVersion)
            .where(CVVersion.id == cv_version.id)
            .options(selectinload(CVVersion.job_target))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, cv_version: CVVersion) -> None:
        await self.session.delete(cv_version)
        await self.session.flush()
