"""Harvest live GoTriple facet counts into the metacat-data JSON store.

Lifts the aggregation query from the GoTriple_stats_queries notebook in the
metacat-code sibling checkout. Run from the metacat-api root:
    uv run src/metacat_api/harvesters/harvest_gotriple.py
"""

import logging
from datetime import datetime

import requests

from metacat_api.harvesters.harvest_common import Facets, apply_catalogue, load_store, report, write_store
from metacat_api.logging_setup import setup_logging

BASE_URL = "https://api.gotriple.eu/api/documents"
FACET_AGGS = {"resource-type": "type", "discipline": "topic", "source": "provider"}
REASONS = {
    "format": "Format is a documented gap in the GoTriple API.",
    "source-2": "GoTriple exposes no secondary source facet.",
    "subjects": "Subjects are a documented gap in the GoTriple API.",
}

logger = logging.getLogger(__name__)


def _fetch(aggs: str) -> list[tuple[str, int]]:
    resp = requests.get(BASE_URL, params={"aggs": aggs}, timeout=60)
    resp.raise_for_status()
    buckets = resp.json().get("aggs", {}).get(aggs, {}).get("buckets", [])
    return [(bucket["key"], bucket["doc_count"]) for bucket in buckets]


def harvest() -> Facets:
    logger.info("GoTriple: Start harvest")
    start = datetime.now()
    facets = {facet: _fetch(aggs) for facet, aggs in FACET_AGGS.items()}
    logger.info(f"GoTriple: End harvest, duration: {datetime.now() - start}")
    return facets


def apply() -> None:
    store = load_store()
    harvested = harvest()
    apply_catalogue(store, "gotriple", harvested, REASONS)
    write_store(store)
    report("gotriple", harvested)


if __name__ == "__main__":
    setup_logging()
    apply()
