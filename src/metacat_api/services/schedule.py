import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

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
