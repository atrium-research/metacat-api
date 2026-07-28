import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from metacat_api.services.harvest import harvest_all

_scheduler: BackgroundScheduler | None = None

logger = logging.getLogger(__name__)


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler
    _scheduler = BackgroundScheduler()
    return _scheduler


def configure_scheduler():
    logger.info("Configuring scheduler")
    trigger = CronTrigger(day_of_week="mon", hour=5, minute=0)
    trigger = CronTrigger(minute="*/5")
    get_scheduler().add_job(
        harvest_all,
        id="harvest_all",
        replace_existing=True,
        trigger=trigger,
        coalesce=True,
    )
    get_scheduler().start()
