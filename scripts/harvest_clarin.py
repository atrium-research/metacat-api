"""Harvest live CLARIN VLO facet counts into a metacat-data JSON store.

Reuses the existing VLO connector from the metacat-code repository (a sibling
checkout) and writes a data directory the json datasource can serve. Only the
clarin-vlo catalogue is real; the other three are copied from the bundled mock
so the API stays fully populated.

Run from the metacat-api root:
    uv run --with requests --with jq python scripts/harvest_clarin.py
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
METACAT_CODE = REPO_ROOT.parent / "metacat-code"
QUERYMODULE_DIR = METACAT_CODE / "CLARIN" / "querymodule"
COLLECTION_PATH = METACAT_CODE / "CLARIN" / "query-collection" / "vlo-query-collection.json"
MOCK_DIR = REPO_ROOT / "src" / "metacat_api" / "mock_data"
OUT_DIR = REPO_ROOT / "data"

SNAPSHOT_TS = "2026-05-03T00:00:00Z"
TOP_N = 50
GAP_REASONS = {
    "discipline": "CLARIN VLO does not expose a discipline facet.",
    "source-2": "CLARIN VLO exposes no secondary source facet.",
}
FACET_ORDER = ["resource-type", "format", "discipline", "source", "source-2", "subjects"]

sys.path.insert(0, str(QUERYMODULE_DIR))
from vlo_querymodule import extractFacetValues  # noqa: E402


def _load(name: str) -> list:
    with (MOCK_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _dump(name: str, data: list) -> None:
    with (OUT_DIR / name).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def harvest() -> dict[str, list[tuple[str, int]]]:
    if not COLLECTION_PATH.exists():
        raise SystemExit(f"metacat-code connector not found at {COLLECTION_PATH}")
    with COLLECTION_PATH.open(encoding="utf-8") as handle:
        collection = json.load(handle)

    raw = extractFacetValues(collection)
    facets: dict[str, list[tuple[str, int]]] = {}
    for facet, entries in raw.items():
        pairs = [(value, count) for entry in entries for value, count in entry.items()]
        pairs.sort(key=lambda item: item[1], reverse=True)
        facets[facet] = pairs[:TOP_N]
    return facets


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    harvested = harvest()
    harvest_ts = datetime.now(UTC).isoformat()

    catalogues = _load("catalogues.json")
    facet_values = [v for v in _load("facet_values.json") if v["catalogue_id"] != "clarin-vlo"]
    facet_exposures = [
        e for e in _load("facet_exposures.json") if e["catalogue_id"] != "clarin-vlo"
    ]

    for facet, pairs in harvested.items():
        for value, count in pairs:
            facet_values.append(
                {
                    "catalogue_id": "clarin-vlo",
                    "facet": facet,
                    "value": value,
                    "count": count,
                    "timestamp": SNAPSHOT_TS,
                }
            )

    for facet in FACET_ORDER:
        if facet in harvested and harvested[facet]:
            pairs = harvested[facet]
            top_value, top_count = pairs[0]
            facet_exposures.append(
                {
                    "catalogue_id": "clarin-vlo",
                    "facet": facet,
                    "status": "exposed",
                    "reason": None,
                    "values_count": len(pairs),
                    "top_value": top_value,
                    "top_value_count": top_count,
                    "total_count": sum(count for _, count in pairs),
                }
            )
        else:
            facet_exposures.append(
                {
                    "catalogue_id": "clarin-vlo",
                    "facet": facet,
                    "status": "gap",
                    "reason": GAP_REASONS.get(facet, "Facet not exposed by CLARIN VLO."),
                    "values_count": None,
                    "top_value": None,
                    "top_value_count": None,
                    "total_count": None,
                }
            )

    resource_total = sum(count for _, count in harvested.get("resource-type", []))
    for catalogue in catalogues:
        if catalogue["id"] == "clarin-vlo":
            if resource_total:
                catalogue["total_resources"] = resource_total
            catalogue["last_harvest_at"] = harvest_ts
            catalogue["harvest_status"] = "live"

    _dump("catalogues.json", catalogues)
    _dump("facet_values.json", facet_values)
    _dump("facet_exposures.json", facet_exposures)
    _dump("vocabularies.json", _load("vocabularies.json"))
    _dump("concepts.json", _load("concepts.json"))
    _dump("mappings.json", _load("mappings.json"))
    _dump("snapshots.json", _load("snapshots.json"))

    print(f"Wrote metacat-data store to {OUT_DIR}")
    for facet in FACET_ORDER:
        pairs = harvested.get(facet)
        if pairs:
            print(f"  clarin-vlo {facet}: {len(pairs)} values, top {pairs[0][0]!r}={pairs[0][1]}")
        else:
            print(f"  clarin-vlo {facet}: gap")


if __name__ == "__main__":
    main()
