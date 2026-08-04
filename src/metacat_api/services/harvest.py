import logging

from anyio import fail_after, to_thread

from metacat_api.harvesters import HARVESTERS

_TIMEOUT = 600

logger = logging.getLogger(__name__)


def harvest_all():
    logger.info("Start harvest all")

    for harvester in HARVESTERS:
        try:
            harvester.apply()
        except Exception as e:
            logger.exception(f"Harvester {harvester.catalogue_id}: error: {e}")
    logger.info("End harvest all")


async def harvest_all_async():
    logger.info("Start harvest all async")
    with fail_after(_TIMEOUT):
        await to_thread.run_sync(harvest_all)


async def harvest(catalogue_id: str):
    harvester = next(iter([harvester for harvester in HARVESTERS if catalogue_id == harvester.catalogue_id]), None)
    if not harvester:
        raise ValueError(f"Unknown catalogue '{catalogue_id}'")
    with fail_after(_TIMEOUT):
        await to_thread.run_sync(harvester.apply)
