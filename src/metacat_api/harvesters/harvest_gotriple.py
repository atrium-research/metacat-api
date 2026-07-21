"""Harvest live GoTriple facet counts into the metacat-data JSON store.

Lifts the aggregation query from the GoTriple_stats_queries notebook in the
metacat-code sibling checkout. Run from the metacat-api root:
    uv run src/metacat_api/harvesters/harvest_gotriple.py
"""

import requests
from harvest_common import Facets, apply_catalogue, load_store, report, write_store

BASE_URL = "https://api.gotriple.eu/api/documents"
FACET_AGGS = {"resource-type": "type", "discipline": "topic", "source": "provider"}
REASONS = {
    "format": "Format is a documented gap in the GoTriple API.",
    "source-2": "GoTriple exposes no secondary source facet.",
    "subjects": "Subjects are a documented gap in the GoTriple API.",
}


def fetch(aggs: str) -> list[tuple[str, int]]:
    resp = requests.get(BASE_URL, params={"aggs": aggs}, timeout=60)
    resp.raise_for_status()
    buckets = resp.json().get("aggs", {}).get(aggs, {}).get("buckets", [])
    return [(bucket["key"], bucket["doc_count"]) for bucket in buckets]


def harvest() -> Facets:
    return {facet: fetch(aggs) for facet, aggs in FACET_AGGS.items()}


def main() -> None:
    harvested = harvest()
    store = load_store()
    apply_catalogue(store, "gotriple", harvested, REASONS)
    write_store(store)
    report("gotriple", harvested)


if __name__ == "__main__":
    main()
