import logging

from metacat_api.harvesters.harvest_ariadne import main as harvest_ariadne_main
from metacat_api.harvesters.harvest_clarin import main as harvest_clarin_main
from metacat_api.harvesters.harvest_gotriple import main as harvest_gotriple_main

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
