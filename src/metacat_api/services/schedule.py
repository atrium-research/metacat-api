import sys

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from metacat_api.harvesters.harvest_ariadne import main as harvest_ariadne_main
from metacat_api.harvesters.harvest_clarin import main as harvest_clarin_main
from metacat_api.harvesters.harvest_gotriple import main as harvest_gotriple_main

_scheduler: BackgroundScheduler | None = None


def harvest_all():
    print("Start harvest")
    try:
        harvest_gotriple_main()
    except Exception as e:
        print(f"harvest_gotriple: error: {e}", file=sys.stderr)
    try:
        harvest_clarin_main()
    except Exception as e:
        print(f"harvest_clarin: error: {e}", file=sys.stderr)
    try:
        harvest_ariadne_main()
    except Exception as e:
        print(f"harvest_ariadne: error: {e}", file=sys.stderr)
    print("End harvest")


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler:
        return _scheduler
    _scheduler = BackgroundScheduler()
    return _scheduler


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
