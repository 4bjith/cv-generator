from typing import Optional, Union
import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db_session
from app.models.job_target import JobTarget
from app.repositories.interfaces.job_target_repository import IJobTargetRepository
from app.repositories.postgres.job_target_repository import PostgresJobTargetRepository
from app.schemas.job_target import (
    JobTargetCreate,
    JobTargetListResponse,
    JobTargetResponse,
    JobTargetUpdate,
)

logger = get_logger("app.services.job_target")


class JobTargetService:
    """Service layer managing candidate job opportunities and target positions."""

    def __init__(self, job_target_repository: IJobTargetRepository) -> None:
        self.job_repo = job_target_repository

    async def create_job_target(
        self,
        user_id: Union[uuid.UUID, str],
        data: JobTargetCreate,
    ) -> JobTargetResponse:
        """Create and persist a new job target opportunity for the authenticated user."""
        uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id

        job = JobTarget(
            user_id=uid,
            title=data.title,
            company_name=data.company_name,
            location=data.location,
            employment_type=data.employment_type,
            job_description=data.job_description,
            source_url=data.source_url,
            user_notes=data.user_notes,
            status=data.status.value if hasattr(data.status, "value") else str(data.status),
        )

        saved = await self.job_repo.create(job)
        logger.info(f"Created job target {saved.id} for user {uid}: '{saved.title}' at '{saved.company_name}'")
        return JobTargetResponse.model_validate(saved)

    async def get_job_target(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> JobTargetResponse:
        """Retrieve a specific job target owned by user_id or raise NotFoundError."""
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )
        return JobTargetResponse.model_validate(job)

    async def list_job_targets(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> JobTargetListResponse:
        """List job targets owned by user_id with search, status filtering and pagination."""
        items, total = await self.job_repo.list_by_user(
            user_id=user_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )
        return JobTargetListResponse(
            items=[JobTargetResponse.model_validate(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_job_target(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
        data: JobTargetUpdate,
    ) -> JobTargetResponse:
        """Update fields of an existing job target."""
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )

        if data.title is not None:
            job.title = data.title
        if data.company_name is not None:
            job.company_name = data.company_name
        if data.location is not None:
            job.location = data.location
        if data.employment_type is not None:
            job.employment_type = data.employment_type
        if data.job_description is not None:
            job.job_description = data.job_description
        if data.source_url is not None:
            job.source_url = data.source_url
        if data.user_notes is not None:
            job.user_notes = data.user_notes
        if data.status is not None:
            job.status = data.status.value if hasattr(data.status, "value") else str(data.status)

        updated = await self.job_repo.update(job)
        logger.info(f"Updated job target {updated.id} for user {user_id}")
        return JobTargetResponse.model_validate(updated)

    async def delete_job_target(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> None:
        """Delete a job target owned by user_id."""
        job = await self.job_repo.get_by_id(job_id=job_id, user_id=user_id)
        if not job:
            raise NotFoundError(
                message="Job target does not exist or you do not have permission to access it.",
                code="JOB_TARGET_NOT_FOUND",
            )

        await self.job_repo.delete(job)
        logger.info(f"Deleted job target {job_id} for user {user_id}")


def get_job_target_service(session: AsyncSession = Depends(get_db_session)) -> JobTargetService:
    """FastAPI dependency injecting JobTargetService initialized with Postgres repository."""
    repository = PostgresJobTargetRepository(session)
    return JobTargetService(repository)
