"""Harvest live GoTriple facet counts into the metacat-data JSON store.

Lifts the aggregation query from the GoTriple_stats_queries notebook in the
metacat-code sibling checkout. Run from the metacat-api root:
    uv run src/metacat_api/harvesters/gotriple.py
"""

import logging
from datetime import datetime

import anyio
import requests

from metacat_api.harvesters.harvester import Harvester
from metacat_api.logging_setup import setup_logging
from metacat_api.models import FacetExposure, FacetExposureStatus, FacetId, RawFacets, raw_facets_adapter

BASE_URL = "https://api.gotriple.eu/api/documents"
FACET_AGGS = {
    FacetId.resource_type: "type",
    FacetId.discipline: "topic",
    FacetId.source: "provider",
}

logger = logging.getLogger(__name__)


def _fetch(aggs: str) -> list[tuple[str, int]]:
    resp = requests.get(
        BASE_URL,
        params={"aggs": aggs, "size": 0},
        timeout=60,
        headers={"User-Agent": "Metacat"},
    )
    resp.raise_for_status()
    buckets = resp.json().get("aggs", {}).get(aggs, {}).get("buckets", [])
    return [(bucket["key"], bucket["doc_count"]) for bucket in buckets]


class GotripleHarvester(Harvester):
    @property
    def catalogue_id(self):
        return "gotriple"

    @property
    def vocabularies(self) -> list[str]:
        return ["triple-vocabulary"]

    @property
    def facet_exposures(self) -> list[FacetExposure]:
        return [
            FacetExposure(
                facet=FacetId.format,
                status=FacetExposureStatus.gap,
                reason="Format is a documented gap in the GoTriple API.",
            ),
            FacetExposure(
                facet=FacetId.source_2,
                status=FacetExposureStatus.gap,
                reason="GoTriple exposes no secondary source facet.",
            ),
            FacetExposure(
                facet=FacetId.subjects,
                status=FacetExposureStatus.gap,
                reason="Subjects are a documented gap in the GoTriple API.",
            ),
        ]

    def harvest(self) -> RawFacets:
        logger.info("GoTriple: Start harvest")
        start = datetime.now()
        facets = raw_facets_adapter.validate_python(
            {facet.name: _fetch(aggs) for facet, aggs in FACET_AGGS.items()},
            extra="forbid",
        )
        logger.info(f"GoTriple: End harvest, duration: {datetime.now() - start}")
        return facets


if __name__ == "__main__":
    setup_logging()
    anyio.run(GotripleHarvester().apply)
