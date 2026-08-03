"""Harvest SSH Open Marketplace facet counts into the metacat-data JSON store.

Reads a full-catalogue item dump published weekly by the community SSHOC/sshompitor
monitoring tool (https://github.com/SSHOC/sshompitor) and tallies all five non-gap
pivot facets from it directly (resource-type, source, subjects, discipline, format),
so every facet reflects the same point in time. item-search's own aggregation only
covers 4 loosely-related facets and has no discipline/format aggregation at all, so
it isn't used here.

By default the newest available snapshot is used. Set SSHOMP_SNAPSHOT_DATE (YYYY-MM-DD)
to use the nearest snapshot at or before that date instead, e.g. to inspect a past state
of the catalogue. Note: this does not backfill a timeseries - each run fully replaces
sshomp's facet_values with whichever single snapshot was selected (same one-moment-per-run
behaviour as the other connectors).

Run from the metacat-api root:
    uv run --with requests python scripts/harvest_sshomp.py
    SSHOMP_SNAPSHOT_DATE=2025-08-01 uv run --with requests python scripts/harvest_sshomp.py
"""

import os
import re
from datetime import UTC, date, datetime

import requests

from metacat_api.harvesters.harvest_common import Facets, apply_catalogue, load_store, report, write_store

SNAPSHOT_INDEX_URL = "https://api.github.com/repos/SSHOC/sshompitor/contents/data"
SNAPSHOT_NAME_RE = re.compile(r"^full_items_(\d+)\.json$")
SNAPSHOT_DATE = os.environ.get("SSHOMP_SNAPSHOT_DATE", "")

CATEGORY_LABELS = {
    "tool-or-service": "Tools & Services",
    "training-material": "Training Materials",
    "publication": "Publications",
    "dataset": "Datasets",
    "workflow": "Workflows",
    "step": "Steps",
}

REASONS = {
    "source-2": "The SSH Open Marketplace exposes no secondary source facet.",
}


def _list_snapshots() -> list[tuple[int, str]]:
    """List every published full-catalogue snapshot, oldest first.

    Queries the GitHub contents API for the sshompitor repo's data/ directory
    and picks out files matching full_items_<unix-timestamp>.json - sshompitor
    publishes one such dump per successful weekly run and does not prune old
    ones, so the directory listing doubles as the available history.

    Returns:
        (unix_timestamp, download_url) pairs, sorted ascending by timestamp.
    """
    resp = requests.get(SNAPSHOT_INDEX_URL, timeout=30)
    resp.raise_for_status()
    return sorted(
        (int(m.group(1)), entry["download_url"])
        for entry in resp.json()
        if (m := SNAPSHOT_NAME_RE.match(entry["name"]))
    )


def _select_snapshot() -> tuple[str, str]:
    """Pick which published snapshot this run should harvest.

    With SSHOMP_SNAPSHOT_DATE unset, takes the newest snapshot available. When
    it's set, takes the newest snapshot whose timestamp falls on or before
    that date, letting a run reconstruct the catalogue's facet counts as of a
    past point in time rather than always tracking the live state.

    Returns:
        A (download_url, snapshot_timestamp_iso) tuple for the chosen snapshot.

    Raises:
        SystemExit: if no snapshots are published, SSHOMP_SNAPSHOT_DATE isn't a
            valid YYYY-MM-DD date, or no snapshot exists at or before it.
    """
    snapshots = _list_snapshots()
    if not snapshots:
        raise SystemExit("No full_items snapshot found in SSHOC/sshompitor data/")
    if not SNAPSHOT_DATE:
        ts, url = snapshots[-1]
    else:
        try:
            cutoff = date.fromisoformat(SNAPSHOT_DATE)
        except ValueError as error:
            raise SystemExit(f"SSHOMP_SNAPSHOT_DATE must be YYYY-MM-DD, got {SNAPSHOT_DATE!r}") from error
        eligible = [(ts, url) for ts, url in snapshots if datetime.fromtimestamp(ts, UTC).date() <= cutoff]
        if not eligible:
            raise SystemExit(f"No snapshot available at or before {SNAPSHOT_DATE}")
        ts, url = eligible[-1]
    return url, datetime.fromtimestamp(ts, UTC).isoformat()


def harvest() -> tuple[Facets, str]:
    """Download the selected snapshot and tally its five pivot facets.

    Each item in the dump is a flat SSH Open Marketplace catalogue record:
        - "category": the item's resource type (tool-or-service, dataset,
          etc.), mapped through CATEGORY_LABELS to the label metacat displays.
        - "source.label": the name of the external system the item was
          aggregated from (its literal key, not a nested "source": {"label"}
          object).
        - "properties": a list of {"type": {"code": ...}, "concept": {"label":
          ...}} entries; the ones with code "keyword", "discipline", and
          "object-format" back the subjects, discipline, and format facets
          respectively. Properties with no concept label (free-text values)
          are skipped, since facets only surface controlled-vocabulary
          values.

    Counts are accumulated per distinct label; source data order does not
    matter and no ranking is applied here (apply_catalogue sorts by count).

    Returns:
        A (facets, snapshot_timestamp_iso) tuple, where facets maps each of
        "resource-type", "source", "subjects", "discipline", "format" to a
        list of (value, count) pairs.
    """
    url, snapshot_ts = _select_snapshot()
    items = requests.get(url, timeout=120).json()

    resource_type: dict[str, int] = {}
    source: dict[str, int] = {}
    subjects: dict[str, int] = {}
    discipline: dict[str, int] = {}
    fmt: dict[str, int] = {}

    for item in items:
        category = item.get("category")
        if category:
            label = CATEGORY_LABELS.get(category, category)
            resource_type[label] = resource_type.get(label, 0) + 1
        src = item.get("source.label")
        if src:
            source[src] = source.get(src, 0) + 1
        for prop in item.get("properties", []):
            code = prop.get("type", {}).get("code")
            label = (prop.get("concept") or {}).get("label")
            if not label:
                continue
            if code == "keyword":
                subjects[label] = subjects.get(label, 0) + 1
            elif code == "discipline":
                discipline[label] = discipline.get(label, 0) + 1
            elif code == "object-format":
                fmt[label] = fmt.get(label, 0) + 1

    facets: Facets = {
        "resource-type": list(resource_type.items()),
        "source": list(source.items()),
        "subjects": list(subjects.items()),
        "discipline": list(discipline.items()),
        "format": list(fmt.items()),
    }
    return facets, snapshot_ts


def main() -> None:
    """Harvest sshomp and replace its facet_values/facet_exposures in the store.

    Delegates the merge itself to apply_catalogue (shared across connectors),
    then overwrites the timestamp on sshomp's rows: apply_catalogue always
    stamps new rows with harvest_common.SNAPSHOT_TS (a fixed constant shared
    by every connector), but sshomp rows should instead carry the timestamp of
    the actual snapshot selected by _select_snapshot, so a backdated run via
    SSHOMP_SNAPSHOT_DATE is reflected correctly in the stored data.
    """
    harvested, snapshot_ts = harvest()
    store = load_store()
    apply_catalogue(store, "sshomp", harvested, REASONS)
    for row in store["facet_values"]:
        if row["catalogue_id"] == "sshomp":
            row["timestamp"] = snapshot_ts
    write_store(store)
    report("sshomp", harvested)


if __name__ == "__main__":
    main()
