import asyncio
import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import async_session_factory
from app.models.autonomous_agent import JobSearchProfile
from app.services.autonomous_agent_service import AutonomousJobAgentService

logger = logging.getLogger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None


async def run_daily_agent_for_active_users() -> None:
    """Executes the daily morning career acquisition run for all active users."""
    logger.info("Executing scheduled morning job discovery and application cycle...")
    try:
        from sqlalchemy import select
        async with async_session_factory() as session:
            query = select(JobSearchProfile).where(
                JobSearchProfile.is_active == True,
                JobSearchProfile.emergency_stopped == False,
            )
            result = await session.execute(query)
            profiles = list(result.scalars().all())

            for prof in profiles:
                try:
                    agent_service = AutonomousJobAgentService(session)
                    report = await agent_service.run_full_cycle(prof.user_id, max_applications=prof.daily_application_cap)
                    await session.commit()
                    logger.info(f"Daily run complete for user {prof.user_id}: {report.jobs_discovered_count} discovered, {report.applications_submitted_count} submitted.")
                except Exception as user_exc:
                    await session.rollback()
                    logger.error(f"Error during daily agent run for user {prof.user_id}: {user_exc}")
    except Exception as exc:
        logger.error(f"Scheduled morning agent job failed: {exc}")


def get_agent_scheduler() -> AsyncIOScheduler:
    """Returns or creates the singleton AsyncIOScheduler for background tasks."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
        # Trigger daily morning job at 07:00 AM IST
        _scheduler.add_job(
            run_daily_agent_for_active_users,
            trigger=CronTrigger(hour=7, minute=0),
            id="daily_morning_career_agent",
            name="Daily Morning Career Acquisition Agent",
            replace_existing=True,
        )
    return _scheduler


def start_agent_scheduler() -> None:
    """Starts the background scheduler if not already running."""
    scheduler = get_agent_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Autonomous Career Agent Scheduler started (Trigger: 07:00 AM IST daily).")


def shutdown_agent_scheduler() -> None:
    """Gracefully shuts down the background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Autonomous Career Agent Scheduler shut down.")
