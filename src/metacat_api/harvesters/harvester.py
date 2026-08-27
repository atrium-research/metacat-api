import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from metacat_api.config import settings
from metacat_api.datasources.store import store, write_store
from metacat_api.models import (
    FacetExposure,
    FacetValue,
    HarvestStatus,
    PivotFacet,
    RawFacets,
    Reasons,
    StatusOverrides,
)
from metacat_api.services.util import now, time_to_str

logger = logging.getLogger(__name__)


def apply_catalogue(
    catalogue_id: str,
    harvested: RawFacets,
    reasons: Reasons,
    status_overrides: StatusOverrides,
) -> None:
    snapshot_ts = time_to_str(now())
    logger.info(f"Start apply catalogue {catalogue_id} for snapshot {snapshot_ts}")
    ranked = {facet: sorted(pairs, key=lambda item: item[1], reverse=True) for facet, pairs in harvested.items()}

    store.facet_values = [v for v in store.facet_values if v.catalogue_id != catalogue_id]
    store.facet_exposures = [e for e in store.facet_exposures if e.catalogue_id != catalogue_id]

    for facet, pairs in ranked.items():
        for value, count in pairs:
            store.facet_values.append(
                FacetValue.model_validate(
                    {
                        "catalogue_id": catalogue_id,
                        "facet": PivotFacet.from_str(facet),
                        "value": value,
                        "count": count,
                        "timestamp": snapshot_ts,
                    },
                    extra="forbid",
                )
            )

    for facet in PivotFacet:
        pairs = ranked.get(facet)
        if pairs:
            status = status_overrides.get(facet, "exposed")
            store.facet_exposures.append(
                FacetExposure.model_validate(
                    {
                        "catalogue_id": catalogue_id,
                        "facet": facet,
                        "status": status,
                        "reason": None if status == "exposed" else reasons.get(facet),
                        "values_count": len(pairs),
                        "total_count": sum(count for _, count in pairs),
                    },
                    extra="forbid",
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
                        "total_count": None,
                    },
                    extra="forbid",
                )
            )

    harvest_ts = datetime.now(UTC)
    for catalogue in store.catalogues:
        if catalogue.id == catalogue_id:
            catalogue.last_harvest_at = harvest_ts
            catalogue.harvest_status = HarvestStatus.live


def report(catalogue_id: str, harvested: RawFacets) -> None:
    logger.info(f"Harvested {catalogue_id} into {settings.json_data_path()}")
    for facet in PivotFacet:
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
    def harvest(self) -> RawFacets: ...

    def apply(self) -> None:
        harvested = self.harvest()
        apply_catalogue(self.catalogue_id, harvested, self.reasons, self.status_overrides)
        write_store()
        report(self.catalogue_id, harvested)
