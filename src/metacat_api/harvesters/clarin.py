"""Harvest live CLARIN VLO facet counts into the metacat-data JSON store.

Reuses the VLO connector from the metacat-code sibling checkout unchanged. Run
from the metacat-api root:
    uv run src/metacat_api/harvesters/harvest_clarin.py
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from metacat_api.harvesters.clarin_lib.vlo_querymodule import extract_facet_values
from metacat_api.harvesters.harvester import Harvester
from metacat_api.logging_setup import setup_logging
from metacat_api.models import PivotFacet, RawFacets, Reasons, StatusOverrides, raw_facets_adapter

logger = logging.getLogger(__name__)


class ClarinHarvester(Harvester):
    @property
    def catalogue_id(self):
        return "clarin-vlo"

    @property
    def reasons(self) -> Reasons:
        return {
            PivotFacet.discipline: "CLARIN VLO does not expose a discipline facet.",
            PivotFacet.source_2: "CLARIN VLO exposes no secondary source facet.",
        }

    @property
    def status_overrides(self) -> StatusOverrides:
        return {}

    def harvest(self) -> RawFacets:
        logger.info("Clarin: Start harvest")
        start = datetime.now()
        with open(Path(__file__).parent / "clarin_lib/vlo-query-collection.json", encoding="utf-8") as handle:
            collection = json.load(handle)

        raw = extract_facet_values(collection)
        facets = raw_facets_adapter.validate_python(
            {
                PivotFacet(facet).name: [(value, count) for entry in entries for value, count in entry.items()]
                for facet, entries in raw.items()
            },
            extra="forbid",
        )
        logger.info(f"Clarin: End harvest, duration: {datetime.now() - start}")
        return facets


if __name__ == "__main__":
    setup_logging()
    ClarinHarvester().apply()
