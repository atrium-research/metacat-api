import logging

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import HTTPException, status

from metacat_api.models import Task
from metacat_api.services.backup import write_backup
from metacat_api.services.harvest import harvest_all

_scheduler: AsyncIOScheduler | None = None

logger = logging.getLogger(__name__)


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler
    _scheduler = AsyncIOScheduler()
    return _scheduler


async def harvest_and_backup():
    await harvest_all()
    await write_backup()


def configure_scheduler():
    logger.info("Configuring scheduler")
    trigger = CronTrigger(day_of_week="mon", hour=5, minute=0)
    get_scheduler().add_job(
        harvest_and_backup,
        id="harvest_and_backup",
        name="Harvest and backup",
        replace_existing=True,
        trigger=trigger,
        coalesce=True,
    )
    get_scheduler().start()


def get_scheduled_tasks():
    return [
        Task.model_validate(
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time,
                "trigger": str(job.trigger),
            },
            extra="forbid",
        )
        for job in get_scheduler().get_jobs()
    ]


def get_scheduled_job(job_id: str) -> Job:
    job = get_scheduler().get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown task '{job_id}'")
    return job


def pause_scheduled_job(job_id: str) -> None:
    job = get_scheduled_job(job_id)
    job.pause()


def resume_scheduled_job(job_id: str) -> None:
    job = get_scheduled_job(job_id)
    job.resume()
