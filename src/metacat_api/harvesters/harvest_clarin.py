"""Harvest live CLARIN VLO facet counts into the metacat-data JSON store.

Reuses the VLO connector from the metacat-code sibling checkout unchanged. Run
from the metacat-api root:
    uv run src/metacat_api/harvesters/harvest_clarin.py
"""

import json
from pathlib import Path

from metacat_api.harvesters.clarin.vlo_querymodule import extract_facet_values
from metacat_api.harvesters.harvest_common import (
    Facets,
    apply_catalogue,
    load_store,
    report,
    write_store,
)

REASONS = {
    "discipline": "CLARIN VLO does not expose a discipline facet.",
    "source-2": "CLARIN VLO exposes no secondary source facet.",
}


def harvest() -> Facets:
    with open(Path(__file__).parent / "clarin/vlo-query-collection.json", encoding="utf-8") as handle:
        collection = json.load(handle)

    raw = extract_facet_values(collection)
    return {
        facet: [(value, count) for entry in entries for value, count in entry.items()] for facet, entries in raw.items()
    }


def main() -> None:
    harvested = harvest()
    store = load_store()
    apply_catalogue(store, "clarin-vlo", harvested, REASONS)
    write_store(store)
    report("clarin-vlo", harvested)


if __name__ == "__main__":
    main()
