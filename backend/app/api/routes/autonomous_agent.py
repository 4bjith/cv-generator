import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.postgres.autonomous_agent_repository import AutonomousAgentRepository
from app.schemas.autonomous_agent import (
    AgentDailyReportResponse,
    AgentRunResult,
    ApplicationRecordResponse,
    ApplicationRecordUpdate,
    DiscoveredJobResponse,
    JobSearchProfileResponse,
    JobSearchProfileUpdate,
    QAMemoryBankItemCreate,
    QAMemoryBankItemResponse,
    RecruiterOutreachResponse,
    RecruiterOutreachUpdate,
)
from app.services.autonomous_agent_service import AutonomousJobAgentService

router = APIRouter(prefix="/agent", tags=["Autonomous Career Agent"])


# ==============================================================================
# Search Profile & Agent Controls
# ==============================================================================

@router.get("/profile", response_model=JobSearchProfileResponse)
async def get_agent_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve the candidate's personal job search configuration and automation settings."""
    service = AutonomousJobAgentService(db)
    profile = await service.ensure_personal_configuration(current_user.id)
    await db.commit()
    return profile


@router.put("/profile", response_model=JobSearchProfileResponse)
async def update_agent_profile(
    payload: JobSearchProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update job search roles, locations, fresher preferences, caps, or automation mode."""
    repo = AutonomousAgentRepository(db)
    updated = await repo.create_or_update_search_profile(
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
    await db.commit()
    return updated


@router.post("/emergency-stop", response_model=JobSearchProfileResponse)
async def emergency_stop_agent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Immediately halt all automated external submissions and job runs."""
    repo = AutonomousAgentRepository(db)
    updated = await repo.create_or_update_search_profile(
        user_id=current_user.id,
        data={"emergency_stopped": True, "is_active": False},
    )
    await db.commit()
    return updated


@router.post("/resume", response_model=JobSearchProfileResponse)
async def resume_agent(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Clear emergency stop and resume normal agent operations."""
    repo = AutonomousAgentRepository(db)
    updated = await repo.create_or_update_search_profile(
        user_id=current_user.id,
        data={"emergency_stopped": False, "is_active": True},
    )
    await db.commit()
    return updated


@router.post("/run-now", response_model=AgentRunResult)
async def run_agent_now(
    max_applications: int = Query(default=3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Trigger an immediate on-demand job discovery, evaluation, tailoring, and application cycle."""
    service = AutonomousJobAgentService(db)
    try:
        report = await service.run_full_cycle(current_user.id, max_applications=max_applications)
        await db.commit()
        return AgentRunResult(
            status="completed",
            message=f"Agent run completed: {report.jobs_discovered_count} discovered, {report.applications_submitted_count} submitted, {report.applications_prepared_count} prepared.",
            jobs_found=report.jobs_discovered_count,
            jobs_shortlisted=report.jobs_shortlisted_count,
            applications_prepared=report.applications_prepared_count,
            applications_submitted=report.applications_submitted_count,
            recruiter_messages_drafted=report.recruiter_outreach_count,
            report=report,
        )
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Autonomous run failed: {exc}")


# ==============================================================================
# Discovered Jobs
# ==============================================================================

@router.get("/jobs", response_model=List[DiscoveredJobResponse])
async def list_discovered_jobs(
    status: Optional[str] = Query(None),
    eligibility: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List discovered job postings with scores, rationale, and eligibility status."""
    repo = AutonomousAgentRepository(db)
    return await repo.list_discovered_jobs(
        user_id=current_user.id,
        status=status,
        eligibility=eligibility,
        limit=limit,
        offset=offset,
    )


@router.post("/jobs/{job_id}/apply", response_model=ApplicationRecordResponse)
async def apply_to_discovered_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Immediately tailor CV, generate cover letter, and execute/prepare application for a discovered job."""
    service = AutonomousJobAgentService(db)
    try:
        application = await service.prepare_and_process_application(current_user.id, job_id)
        await db.commit()
        return application
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process application: {exc}")


# ==============================================================================
# Application Records & Tracking
# ==============================================================================

@router.get("/applications", response_model=List[ApplicationRecordResponse])
async def list_applications(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List all tracked applications, submission confirmation codes, and screenshots."""
    repo = AutonomousAgentRepository(db)
    return await repo.list_application_records(
        user_id=current_user.id,
        status=status,
        limit=limit,
        offset=offset,
    )


# ==============================================================================
# Recruiter Outreach & Follow-Ups
# ==============================================================================

@router.get("/outreach", response_model=List[RecruiterOutreachResponse])
async def list_recruiter_outreach(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List drafted and sent recruiter outreach messages (LinkedIn notes, cold emails)."""
    repo = AutonomousAgentRepository(db)
    return await repo.list_recruiter_outreach(user_id=current_user.id, status=status)


@router.patch("/outreach/{outreach_id}", response_model=RecruiterOutreachResponse)
async def update_recruiter_outreach(
    outreach_id: uuid.UUID,
    payload: RecruiterOutreachUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Edit message draft or mark recruiter outreach as sent / replied."""
    repo = AutonomousAgentRepository(db)
    updated = await repo.update_outreach_status(
        outreach_id=outreach_id,
        user_id=current_user.id,
        status=payload.status or "drafted",
        reply_notes=payload.reply_notes,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Outreach target not found.")
    await db.commit()
    return updated


# ==============================================================================
# QA Memory Bank
# ==============================================================================

@router.get("/qa-bank", response_model=List[QAMemoryBankItemResponse])
async def list_qa_items(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List verified Question-Answering Memory Bank items for application forms."""
    repo = AutonomousAgentRepository(db)
    service = AutonomousJobAgentService(db)
    await service.ensure_personal_configuration(current_user.id)
    await db.commit()
    return await repo.list_qa_items(user_id=current_user.id, category=category)


@router.post("/qa-bank", response_model=QAMemoryBankItemResponse, status_code=status.HTTP_201_CREATED)
async def create_qa_item(
    payload: QAMemoryBankItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Add a new verified question pattern and answer to the QA Memory Bank."""
    from app.models.autonomous_agent import QAMemoryBankItem
    repo = AutonomousAgentRepository(db)
    item = QAMemoryBankItem(
        user_id=current_user.id,
        category=payload.category,
        question_pattern=payload.question_pattern,
        answer_value=payload.answer_value,
        is_confirmed=payload.is_confirmed,
        user_notes=payload.user_notes,
    )
    saved = await repo.create_qa_item(item)
    await db.commit()
    return saved


@router.delete("/qa-bank/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qa_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Delete an item from the QA Memory Bank."""
    repo = AutonomousAgentRepository(db)
    deleted = await repo.delete_qa_item(item_id=item_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="QA Item not found.")
    await db.commit()
    return None


# ==============================================================================
# Daily Reports
# ==============================================================================

@router.get("/reports/latest", response_model=Optional[AgentDailyReportResponse])
async def get_latest_daily_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the latest morning career agent report briefing."""
    repo = AutonomousAgentRepository(db)
    return await repo.get_latest_daily_report(user_id=current_user.id)


@router.get("/reports", response_model=List[AgentDailyReportResponse])
async def list_daily_reports(
    limit: int = Query(14, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List historical daily career agent reports."""
    repo = AutonomousAgentRepository(db)
    return await repo.list_daily_reports(user_id=current_user.id, limit=limit)
