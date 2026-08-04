import json
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path

from pydantic_core import to_jsonable_python

from metacat_api.config import settings
from metacat_api.models import (
    COLLECTIONS,
    FACETS,
    CollectionValues,
    FacetExposure,
    Facets,
    FacetValue,
    HarvestStatus,
    Reasons,
    StatusOverrides,
    Store,
)

OUT_DIR = Path(settings.json_data_dir).resolve()

SNAPSHOT_TS = "2026-05-03T00:00:00Z"

logger = logging.getLogger(__name__)


def _read(directory: Path, name: str) -> CollectionValues:
    with (directory / f"{name}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


def load_store() -> Store:
    loaded = {name: _read(OUT_DIR, name) for name in COLLECTIONS}
    return Store.model_validate(loaded)


def write_store(store: Store) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in COLLECTIONS:
        with (OUT_DIR / f"{name}.json").open("w", encoding="utf-8") as handle:
            json.dump(store.get(name), handle, indent=2, ensure_ascii=False, default=to_jsonable_python)
            handle.write("\n")


def apply_catalogue(
    store: Store,
    catalogue_id: str,
    harvested: Facets,
    reasons: Reasons,
    status_overrides: StatusOverrides,
) -> None:
    ranked = {
        facet: sorted(pairs, key=lambda item: item[1], reverse=True) for facet, pairs in harvested.items() if pairs
    }

    store.facet_values = [v for v in store.facet_values if v.catalogue_id != catalogue_id]
    store.facet_exposures = [e for e in store.facet_exposures if e.catalogue_id != catalogue_id]

    for facet, pairs in ranked.items():
        for value, count in pairs:
            store.facet_values.append(
                FacetValue.model_validate(
                    {
                        "catalogue_id": catalogue_id,
                        "facet": facet,
                        "value": value,
                        "count": count,
                        "timestamp": SNAPSHOT_TS,
                    }
                )
            )

    for facet in FACETS:
        pairs = ranked.get(facet)
        if pairs:
            status = status_overrides.get(facet, "exposed")
            top_value, top_count = pairs[0]
            store.facet_exposures.append(
                FacetExposure.model_validate(
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
            )
        else:
            store.facet_exposures.append(
                FacetExposure.model_validate(
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
            )

    harvest_ts = datetime.now(UTC)
    for catalogue in store.catalogues:
        if catalogue.id == catalogue_id:
            catalogue.last_harvest_at = harvest_ts
            catalogue.harvest_status = HarvestStatus.live


def report(catalogue_id: str, harvested: Facets) -> None:
    logger.info(f"Harvested {catalogue_id} into {OUT_DIR}")
    for facet in FACETS:
        pairs = harvested.get(facet)
        if pairs:
            top = max(pairs, key=lambda item: item[1])
            logger.info(f"{catalogue_id}: {facet}: {len(pairs)} values, top {top[0]!r}={top[1]}")
        else:
            logger.info(f"{catalogue_id}: {facet}: gap")


class Harvester(ABC):
    @property
    @abstractmethod
    def catalogue_id(self) -> str: ...

    @property
    @abstractmethod
    def reasons(self) -> Reasons: ...

    @property
    @abstractmethod
    def status_overrides(self) -> StatusOverrides: ...

    @abstractmethod
    def harvest(self) -> Facets: ...

    def apply(self) -> None:
        store = load_store()
        harvested = self.harvest()
        apply_catalogue(store, self.catalogue_id, harvested, self.reasons, self.status_overrides)
        write_store(store)
        report(self.catalogue_id, harvested)
