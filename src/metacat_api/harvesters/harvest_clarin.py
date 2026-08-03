"""Harvest live CLARIN VLO facet counts into the metacat-data JSON store.

Reuses the VLO connector from the metacat-code sibling checkout unchanged. Run
from the metacat-api root:
    uv run src/metacat_api/harvesters/harvest_clarin.py
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from metacat_api.harvesters.clarin.vlo_querymodule import extract_facet_values
from metacat_api.harvesters.harvest_common import (
    Facets,
    apply_catalogue,
    load_store,
    report,
    write_store,
)
from metacat_api.logging_setup import setup_logging

REASONS = {
    "discipline": "CLARIN VLO does not expose a discipline facet.",
    "source-2": "CLARIN VLO exposes no secondary source facet.",
}

logger = logging.getLogger(__name__)


def harvest() -> Facets:
    logger.info("Clarin: Start harvest")
    start = datetime.now()
    with open(Path(__file__).parent / "clarin/vlo-query-collection.json", encoding="utf-8") as handle:
        collection = json.load(handle)

    raw = extract_facet_values(collection)
    facets = {
        facet: [(value, count) for entry in entries for value, count in entry.items()] for facet, entries in raw.items()
    }
    logger.info(f"Clarin: End harvest, duration: {datetime.now() - start}")
    return facets


def apply() -> None:
    store = load_store()
    harvested = harvest()
    apply_catalogue(store, "clarin-vlo", harvested, REASONS)
    write_store(store)
    report("clarin-vlo", harvested)


if __name__ == "__main__":
    setup_logging()
    apply()
