import logging

from anyio import fail_after

from metacat_api.harvesters import HARVESTERS

_TIMEOUT = 600

logger = logging.getLogger(__name__)


async def harvest_all():
    logger.info("Start harvest all")
    for harvester in HARVESTERS:
        with fail_after(_TIMEOUT):
            await harvester.apply()
    logger.info("End harvest all")


async def harvest(catalogue_id: str):
    harvester = next((harvester for harvester in HARVESTERS if catalogue_id == harvester.catalogue_id), None)
    if not harvester:
        raise ValueError(f"Unknown catalogue '{catalogue_id}'")
    with fail_after(_TIMEOUT):
        await harvester.apply()
