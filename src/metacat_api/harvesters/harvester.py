import logging
import uuid
from abc import ABC, abstractmethod

from metacat_api.config import settings
from metacat_api.datasources.store import store, write_store
from metacat_api.models import (
    CatalogueVersion,
    FacetExposure,
    FacetId,
    FacetValue,
    HarvestStatus,
    RawFacets,
)
from metacat_api.services.util import now, time_to_str

logger = logging.getLogger(__name__)


def _report(catalogue_id: str, harvested: RawFacets) -> None:
    logger.info(f"Harvested {catalogue_id} into {settings.json_data_path()}")
    for facet in FacetId:
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
    def vocabularies(self) -> list[str]: ...

    @property
    @abstractmethod
    def facet_exposures(self) -> list[FacetExposure]: ...

    @abstractmethod
    def harvest(self) -> RawFacets: ...

    def apply_catalogue(self, harvested: RawFacets) -> None:
        version_ts = now()
        logger.info(f"Start apply catalogue {self.catalogue_id} for version {time_to_str(version_ts)}")
        ranked = {facet: sorted(pairs, key=lambda item: item[1], reverse=True) for facet, pairs in harvested.items()}

        store.facet_values = [v for v in store.facet_values if v.catalogue_id != self.catalogue_id]

        new_version = CatalogueVersion(
            catalogue_id=self.catalogue_id,
            version_id=uuid.uuid4(),
            total_resources=0,
            harvest_at=version_ts,
            harvest_status=HarvestStatus.success,
            vocabularies=self.vocabularies,
        )

        store.catalogues_versions.append(new_version)

        for facet, pairs in ranked.items():
            for value, count in pairs:
                store.facet_values.append(
                    FacetValue(
                        catalogue_id=self.catalogue_id,
                        facet=FacetId.from_str(facet),
                        value=value,
                        count=count,
                        timestamp=version_ts,
                    )
                )

        for facet_id in FacetId:
            facet_exposure = next(
                (fe for fe in self.facet_exposures if fe.facet == facet_id),
                FacetExposure(facet=facet_id),
            )
            new_version.facet_exposures.append(facet_exposure)

            pairs = ranked.get(facet_id)
            if pairs:
                facet_exposure.values_count = len(pairs)
                facet_exposure.total_count = sum(count for _, count in pairs)

        new_version.total_resources = sum(facet_exposure.total_count or 0 for facet_exposure in new_version.facet_exposures)

    def apply(self) -> None:
        harvested = self.harvest()
        self.apply_catalogue(harvested)
        write_store()
        _report(self.catalogue_id, harvested)
