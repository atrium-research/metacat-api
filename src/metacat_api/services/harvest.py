import logging

from anyio import fail_after, to_thread

from metacat_api.harvesters.ariadne import AriadneHarvester
from metacat_api.harvesters.clarin import ClarinHarvester
from metacat_api.harvesters.gotriple import GotripleHarvester
from metacat_api.harvesters.sshomp import SshompHarvester

_TIMEOUT = 600

logger = logging.getLogger(__name__)


HARVESTERS = {
    "gotriple": GotripleHarvester().apply,
    "ariadne": AriadneHarvester().apply,
    "sshomp": SshompHarvester().apply,
    "clarin": ClarinHarvester().apply,
}


def harvest_all():
    logger.info("Start harvest all")

    for harvester_id, harvester_function in HARVESTERS.items():
        try:
            harvester_function()
        except Exception as e:
            logger.exception(f"Harvester {harvester_id}: error: {e}")
    logger.info("End harvest all")


async def harvest_all_async():
    logger.info("Start harvest all async")
    with fail_after(_TIMEOUT):
        await to_thread.run_sync(harvest_all)


async def harvest(catalogue_id: str):
    if catalogue_id not in HARVESTERS:
        raise ValueError(f"Unknown catalogue '{catalogue_id}'")
    with fail_after(_TIMEOUT):
        harvester_function = HARVESTERS[catalogue_id]
        await to_thread.run_sync(harvester_function)
