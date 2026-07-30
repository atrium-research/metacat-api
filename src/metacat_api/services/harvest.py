import logging

from anyio import fail_after, to_thread

from metacat_api.harvesters import harvest_ariadne, harvest_clarin, harvest_gotriple
from metacat_api.harvesters.harvest_ariadne import main as harvest_ariadne_main
from metacat_api.harvesters.harvest_clarin import main as harvest_clarin_main
from metacat_api.harvesters.harvest_gotriple import main as harvest_gotriple_main

_TIMEOUT = 600

logger = logging.getLogger(__name__)


def harvest_all():
    logger.info("Start harvest")
    try:
        harvest_gotriple_main()
    except Exception as e:
        logger.exception(f"harvest_gotriple: error: {e}")
    try:
        harvest_clarin_main()
    except Exception as e:
        logger.exception(f"harvest_clarin: error: {e}")
    try:
        harvest_ariadne_main()
    except Exception as e:
        logger.exception(f"harvest_ariadne: error: {e}")
    logger.info("End harvest")


async def harvest(catalogue_id: str):
    with fail_after(_TIMEOUT):
        match catalogue_id:
            case "ariadne":
                await to_thread.run_sync(harvest_ariadne.main)
            case "gotriple":
                await to_thread.run_sync(harvest_gotriple.main)
            case "clarin":
                await to_thread.run_sync(harvest_clarin.main)
            case _:
                raise ValueError(f"Unknown catalogue '{catalogue_id}'")
