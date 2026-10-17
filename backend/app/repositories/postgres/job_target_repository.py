import uuid
from typing import List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_target import JobTarget
from app.repositories.interfaces.job_target_repository import IJobTargetRepository


class PostgresJobTargetRepository(IJobTargetRepository):
    """PostgreSQL / SQLAlchemy implementation of IJobTargetRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, job_target: JobTarget) -> JobTarget:
        self.session.add(job_target)
        await self.session.flush()
        await self.session.refresh(job_target)
        return job_target

    async def get_by_id(
        self,
        job_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[JobTarget]:
        if isinstance(job_id, str):
            try:
                job_id = uuid.UUID(job_id)
            except ValueError:
                return None
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        stmt = select(JobTarget).where(
            JobTarget.id == job_id,
            JobTarget.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[JobTarget], int]:
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return [], 0

        # Base filter
        filters = [JobTarget.user_id == user_id]

        if status:
            filters.append(JobTarget.status == status)

        if search:
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    JobTarget.title.ilike(search_pattern),
                    JobTarget.company_name.ilike(search_pattern),
                    JobTarget.location.ilike(search_pattern),
                )
            )

        # Count query
        count_stmt = select(func.count(JobTarget.id)).where(*filters)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data query with pagination
        stmt = (
            select(JobTarget)
            .where(*filters)
            .order_by(JobTarget.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def update(self, job_target: JobTarget) -> JobTarget:
        self.session.add(job_target)
        await self.session.flush()
        await self.session.refresh(job_target)
        return job_target

    async def delete(self, job_target: JobTarget) -> None:
        await self.session.delete(job_target)
        await self.session.flush()
