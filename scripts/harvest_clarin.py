"""Harvest live CLARIN VLO facet counts into the metacat-data JSON store.

Reuses the VLO connector from the metacat-code sibling checkout unchanged. Run
from the metacat-api root:
    uv run scripts/harvest_clarin.py
"""

import json
import sys
from pathlib import Path

from harvest_common import Facets, apply_catalogue, load_store, report, write_store

METACAT_CODE = Path(__file__).resolve().parents[2] / "metacat-code"
QUERYMODULE_DIR = METACAT_CODE / "CLARIN" / "querymodule"
COLLECTION_PATH = METACAT_CODE / "CLARIN" / "query-collection" / "vlo-query-collection.json"

REASONS = {
    "discipline": "CLARIN VLO does not expose a discipline facet.",
    "source-2": "CLARIN VLO exposes no secondary source facet.",
}

sys.path.insert(0, str(QUERYMODULE_DIR))
from vlo_querymodule import extractFacetValues  # noqa: E402


def harvest() -> Facets:
    if not COLLECTION_PATH.exists():
        raise SystemExit(f"metacat-code connector not found at {COLLECTION_PATH}")
    with COLLECTION_PATH.open(encoding="utf-8") as handle:
        collection = json.load(handle)

    raw = extractFacetValues(collection)
    return {
        facet: [(value, count) for entry in entries for value, count in entry.items()]
        for facet, entries in raw.items()
    }


def main() -> None:
    harvested = harvest()
    store = load_store()
    apply_catalogue(store, "clarin-vlo", harvested, REASONS)
    write_store(store)
    report("clarin-vlo", harvested)


if __name__ == "__main__":
    main()
