from typing import Any, Dict, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.cv import (
    CVVersionCreate,
    CVVersionDuplicate,
    CVVersionListResponse,
    CVVersionResponse,
    CVVersionStatus,
    CVVersionUpdate,
)
from app.services.cv_service import CVService, get_cv_service

router = APIRouter(prefix="/cv/versions", tags=["CV Versions"])


@router.get(
    "",
    response_model=CVVersionListResponse,
    summary="List CV versions",
    description="Retrieve paginated list of CV versions owned by the authenticated user with optional status, job target, and search filters.",
)
async def list_versions(
    status: Optional[CVVersionStatus] = Query(None, description="Filter by version status ('draft', 'ready', 'archived')"),
    job_target_id: Optional[uuid.UUID] = Query(None, description="Filter by linked job target ID"),
    search: Optional[str] = Query(None, description="Search query matching CV version name"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionListResponse:
    status_str = status.value if status else None
    return await service.list_versions(
        user_id=current_user.id,
        status=status_str,
        job_target_id=job_target_id,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=CVVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create CV version",
    description="Create a new independent CV version snapshot from the user's master CandidateProfile.",
)
async def create_version(
    data: CVVersionCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionResponse:
    return await service.create_version_from_profile(current_user.id, data)


@router.get(
    "/{version_id}",
    response_model=CVVersionResponse,
    summary="Get CV version",
    description="Retrieve a single CV version with full content snapshot owned by the authenticated user.",
)
async def get_version(
    version_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionResponse:
    return await service.get_version(current_user.id, version_id)


@router.patch(
    "/{version_id}",
    response_model=CVVersionResponse,
    summary="Update CV version",
    description="Update permitted metadata and/or version-specific content snapshot.",
)
async def update_version(
    version_id: uuid.UUID,
    data: CVVersionUpdate,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionResponse:
    return await service.update_version(current_user.id, version_id, data)


@router.post(
    "/{version_id}/duplicate",
    response_model=CVVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate CV version",
    description="Clone an existing CV version into a new independently persisted record with a deep-copied snapshot.",
)
async def duplicate_version(
    version_id: uuid.UUID,
    data: Optional[CVVersionDuplicate] = None,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionResponse:
    payload = data or CVVersionDuplicate()
    return await service.duplicate_version(current_user.id, version_id, payload)


@router.post(
    "/{version_id}/archive",
    response_model=CVVersionResponse,
    summary="Archive CV version",
    description="Transition CV version status to 'archived'.",
)
async def archive_version(
    version_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionResponse:
    return await service.archive_version(current_user.id, version_id)


@router.post(
    "/{version_id}/restore",
    response_model=CVVersionResponse,
    summary="Restore CV version",
    description="Transition an archived CV version status back to 'draft'.",
)
async def restore_version(
    version_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> CVVersionResponse:
    return await service.restore_version(current_user.id, version_id)


@router.delete(
    "/{version_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete CV version",
    description="Delete a CV version owned by the authenticated user.",
)
async def delete_version(
    version_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> None:
    await service.delete_version(current_user.id, version_id)


@router.get(
    "/{version_id}/json-resume",
    response_model=Dict[str, Any],
    summary="Export standard JSON Resume",
    description="Export CV version formatted as standard JSON Resume schema, stripping product extensions.",
)
async def export_json_resume(
    version_id: uuid.UUID,
    apply_visibility: bool = Query(False, description="Whether to filter out hidden sections and items according to presentation settings"),
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> Dict[str, Any]:
    return await service.export_json_resume(
        user_id=current_user.id,
        version_id=version_id,
        apply_visibility=apply_visibility,
    )


@router.get(
    "/{version_id}/export/pdf",
    summary="Export CV version to PDF",
    description="Generate and download a high-resolution, searchable vector PDF of the CV version.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Downloadable PDF document.",
        }
    },
)
async def export_pdf(
    version_id: uuid.UUID,
    template: Optional[str] = Query(None, description="Optional template override"),
    page_size: Optional[str] = Query(None, description="Optional page size override ('a4', 'letter')"),
    spacing: Optional[str] = Query(None, description="Optional spacing density ('compact', 'normal', 'relaxed')"),
    color_scheme: Optional[str] = Query(None, description="Optional color scheme override"),
    typography: Optional[str] = Query(None, description="Optional typography override ('sans', 'serif', 'mono')"),
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> Response:
    overrides = {}
    if template:
        overrides["template"] = template
    if page_size:
        overrides["page_size"] = page_size
    if spacing:
        overrides["spacing"] = spacing
    if color_scheme:
        overrides["color_scheme"] = color_scheme
    if typography:
        overrides["typography"] = typography

    pdf_bytes, filename = await service.export_pdf(
        user_id=current_user.id,
        version_id=version_id,
        overrides=overrides if overrides else None,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@router.get(
    "/{version_id}/export/docx",
    summary="Export CV version to DOCX",
    description="Generate and download an editable Microsoft Word (.docx) document of the CV version.",
    responses={
        200: {
            "content": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}},
            "description": "Downloadable Microsoft Word document.",
        }
    },
)
async def export_docx(
    version_id: uuid.UUID,
    template: Optional[str] = Query(None, description="Optional template override"),
    page_size: Optional[str] = Query(None, description="Optional page size override ('a4', 'letter')"),
    spacing: Optional[str] = Query(None, description="Optional spacing density ('compact', 'normal', 'relaxed')"),
    color_scheme: Optional[str] = Query(None, description="Optional color scheme override"),
    typography: Optional[str] = Query(None, description="Optional typography override ('sans', 'serif', 'mono')"),
    current_user: UserResponse = Depends(get_current_user),
    service: CVService = Depends(get_cv_service),
) -> Response:
    overrides = {}
    if template:
        overrides["template"] = template
    if page_size:
        overrides["page_size"] = page_size
    if spacing:
        overrides["spacing"] = spacing
    if color_scheme:
        overrides["color_scheme"] = color_scheme
    if typography:
        overrides["typography"] = typography

    docx_bytes, filename = await service.export_docx(
        user_id=current_user.id,
        version_id=version_id,
        overrides=overrides if overrides else None,
    )
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
