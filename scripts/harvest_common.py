"""Shared helpers for the harvest scripts.

Each connector lifts the query logic out of a metacat-code notebook or module,
returns facet counts as {facet: [(value, count), ...]}, and merges them into a
metacat-data JSON store the json datasource can serve. Connectors compose: the
store is loaded from an existing data/ directory when present, so running two
connectors in a row keeps both catalogues real.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MOCK_DIR = REPO_ROOT / "src" / "metacat_api" / "mock_data"
OUT_DIR = REPO_ROOT / "data"

SNAPSHOT_TS = "2026-05-03T00:00:00Z"
FACET_ORDER = ["resource-type", "format", "discipline", "source", "source-2", "subjects"]
TOP_N = 50
COLLECTIONS = [
    "catalogues",
    "facet_values",
    "facet_exposures",
    "vocabularies",
    "concepts",
    "mappings",
    "snapshots",
]

Facets = dict[str, list[tuple[str, int]]]


def _read(directory: Path, name: str) -> list:
    with (directory / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def load_store() -> dict[str, list]:
    base = OUT_DIR if (OUT_DIR / "catalogues.json").exists() else MOCK_DIR
    return {name: _read(base, name) for name in COLLECTIONS}


def write_store(store: dict[str, list]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in COLLECTIONS:
        with (OUT_DIR / f"{name}.json").open("w", encoding="utf-8") as handle:
            json.dump(store[name], handle, indent=2, ensure_ascii=False)
            handle.write("\n")


def apply_catalogue(
    store: dict[str, list],
    catalogue_id: str,
    harvested: Facets,
    reasons: dict[str, str],
    status_overrides: dict[str, str] | None = None,
) -> None:
    status_overrides = status_overrides or {}
    capped = {
        facet: sorted(pairs, key=lambda item: item[1], reverse=True)[:TOP_N]
        for facet, pairs in harvested.items()
        if pairs
    }

    store["facet_values"] = [v for v in store["facet_values"] if v["catalogue_id"] != catalogue_id]
    store["facet_exposures"] = [
        e for e in store["facet_exposures"] if e["catalogue_id"] != catalogue_id
    ]

    for facet, pairs in capped.items():
        for value, count in pairs:
            store["facet_values"].append(
                {
                    "catalogue_id": catalogue_id,
                    "facet": facet,
                    "value": value,
                    "count": count,
                    "timestamp": SNAPSHOT_TS,
                }
            )

    for facet in FACET_ORDER:
        pairs = capped.get(facet)
        if pairs:
            status = status_overrides.get(facet, "exposed")
            top_value, top_count = pairs[0]
            store["facet_exposures"].append(
                {
                    "catalogue_id": catalogue_id,
                    "facet": facet,
                    "status": status,
                    "reason": None if status == "exposed" else reasons.get(facet),
                    "values_count": len(pairs),
                    "top_value": top_value,
                    "top_value_count": top_count,
                    "total_count": sum(count for _, count in pairs),
                }
            )
        else:
            store["facet_exposures"].append(
                {
                    "catalogue_id": catalogue_id,
                    "facet": facet,
                    "status": "gap",
                    "reason": reasons.get(facet, "Facet not exposed by the source."),
                    "values_count": None,
                    "top_value": None,
                    "top_value_count": None,
                    "total_count": None,
                }
            )

    harvest_ts = datetime.now(UTC).isoformat()
    for catalogue in store["catalogues"]:
        if catalogue["id"] == catalogue_id:
            catalogue["last_harvest_at"] = harvest_ts
            catalogue["harvest_status"] = "live"


def report(catalogue_id: str, harvested: Facets) -> None:
    print(f"Harvested {catalogue_id} into {OUT_DIR}")
    for facet in FACET_ORDER:
        pairs = harvested.get(facet)
        if pairs:
            top = max(pairs, key=lambda item: item[1])
            print(f"  {facet}: {len(pairs)} values, top {top[0]!r}={top[1]}")
        else:
            print(f"  {facet}: gap")
