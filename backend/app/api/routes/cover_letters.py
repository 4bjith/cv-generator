import asyncio
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db_session
from app.models.cover_letter import CoverLetter
from app.schemas.auth import UserResponse
from app.schemas.cover_letter import (
    CoverLetterResponse,
    CoverLetterSummary,
    GenerateCoverLetterRequest,
    RegenerateCoverLetterRequest,
    UpdateCoverLetterRequest,
)
from app.services.cover_letter_service import CoverLetterService
from app.services.export.cover_letter_exporter import (
    generate_cover_letter_docx,
    generate_cover_letter_pdf,
    get_sanitized_cover_letter_filename,
)

router = APIRouter()


def get_cover_letter_service(
    session: AsyncSession = Depends(get_db_session),
) -> CoverLetterService:
    """Dependency provider for CoverLetterService."""
    return CoverLetterService(session)


@router.post(
    "/generate",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an evidence-grounded cover letter",
    description="Generate a tailored cover letter from target job requirements and verified candidate profile facts.",
)
async def generate_cover_letter(
    request: GenerateCoverLetterRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> CoverLetterResponse:
    return await service.generate_cover_letter(
        user_id=current_user.id,
        request=request,
    )


@router.get(
    "",
    response_model=Dict[str, Any],
    summary="List cover letters for the current user",
    description="List all cover letters with optional status, job_target, and text search filters.",
)
async def list_cover_letters(
    status: Optional[str] = Query(None, description="Filter by status ('draft', 'ready', 'archived')"),
    job_id: Optional[uuid.UUID] = Query(None, description="Filter by target JobTarget ID"),
    search: Optional[str] = Query(None, description="Search term for letter name or company"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> Dict[str, Any]:
    items, total = await service.list_cover_letters(
        user_id=current_user.id,
        status=status,
        job_target_id=job_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [item.model_dump() for item in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/{letter_id}",
    response_model=CoverLetterResponse,
    summary="Get single cover letter detail",
    description="Fetch a specific cover letter by ID with full body paragraphs and evidence provenance.",
)
async def get_cover_letter(
    letter_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> CoverLetterResponse:
    return await service.get_cover_letter(
        letter_id=letter_id,
        user_id=current_user.id,
    )


@router.put(
    "/{letter_id}",
    response_model=CoverLetterResponse,
    summary="Update an existing cover letter",
    description="Edit recipient details, salutation, paragraphs, or status of a cover letter draft.",
)
async def update_cover_letter(
    letter_id: uuid.UUID,
    request: UpdateCoverLetterRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> CoverLetterResponse:
    return await service.update_cover_letter(
        letter_id=letter_id,
        user_id=current_user.id,
        request=request,
    )


@router.post(
    "/{letter_id}/regenerate",
    response_model=CoverLetterResponse,
    summary="Regenerate cover letter with adjusted parameters",
    description="Re-synthesize draft with updated instructions or tone. Optionally preserves prior version.",
)
async def regenerate_cover_letter(
    letter_id: uuid.UUID,
    request: RegenerateCoverLetterRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> CoverLetterResponse:
    return await service.regenerate_cover_letter(
        letter_id=letter_id,
        user_id=current_user.id,
        request=request,
    )


@router.post(
    "/{letter_id}/duplicate",
    response_model=CoverLetterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a cover letter",
    description="Create an independent copy of an existing cover letter draft.",
)
async def duplicate_cover_letter(
    letter_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> CoverLetterResponse:
    return await service.duplicate_cover_letter(
        letter_id=letter_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{letter_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a cover letter",
    description="Permanently delete a cover letter artifact belonging to the current user.",
)
async def delete_cover_letter(
    letter_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> Dict[str, Any]:
    await service.delete_cover_letter(
        letter_id=letter_id,
        user_id=current_user.id,
    )
    return {
        "message": "Cover letter deleted successfully",
        "id": str(letter_id),
    }


@router.get(
    "/{letter_id}/export/pdf",
    summary="Export cover letter to PDF",
    description="Download a formatted professional PDF version of the cover letter.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Downloadable PDF document.",
        }
    },
)
async def export_pdf(
    letter_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> Response:
    letter = await service.cover_letter_repo.get_by_id(letter_id=letter_id, user_id=current_user.id)
    if not letter:
        raise NotFoundError(
            message="Cover letter not found or you do not have permission to access it.",
            code="COVER_LETTER_NOT_FOUND",
        )

    buffer = await asyncio.to_thread(generate_cover_letter_pdf, letter)
    filename = get_sanitized_cover_letter_filename(letter.name, "pdf")

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/{letter_id}/export/docx",
    summary="Export cover letter to DOCX",
    description="Download an editable Microsoft Word (.docx) document of the cover letter.",
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}},
            "description": "Downloadable Microsoft Word document.",
        }
    },
)
async def export_docx(
    letter_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CoverLetterService = Depends(get_cover_letter_service),
) -> Response:
    letter = await service.cover_letter_repo.get_by_id(letter_id=letter_id, user_id=current_user.id)
    if not letter:
        raise NotFoundError(
            message="Cover letter not found or you do not have permission to access it.",
            code="COVER_LETTER_NOT_FOUND",
        )

    buffer = await asyncio.to_thread(generate_cover_letter_docx, letter)
    filename = get_sanitized_cover_letter_filename(letter.name, "docx")

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
