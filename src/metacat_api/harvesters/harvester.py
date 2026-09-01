import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from metacat_api.config import settings
from metacat_api.datasources.store import store, update_catalogue_version, write_facet_values
from metacat_api.models import (
    CatalogueVersion,
    FacetExposure,
    FacetId,
    FacetValue,
    HarvestStatus,
    RawFacets,
)
from metacat_api.services.export import clear_computed_ao_cat
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

    def _create_catalogue_version(self) -> CatalogueVersion:
        version_id = uuid.uuid4()
        version_ts = now()
        logger.info(f"New version {self.catalogue_id} / {version_id} at {time_to_str(version_ts)}")

        new_version = CatalogueVersion(
            catalogue_id=self.catalogue_id,
            version_id=version_id,
            harvest_at=version_ts,
            vocabularies=self.vocabularies,
        )
        store.catalogues_versions.append(new_version)
        return new_version

    def _add_version(self, harvested: RawFacets | None) -> CatalogueVersion:
        new_version = self._create_catalogue_version()

        if not harvested:
            logger.error("No facet harvested")
            new_version.harvest_status = HarvestStatus.error
            new_version.harvest_error = "No facet harvested"
            return new_version

        new_facet_values = []
        ranked = {facet: sorted(pairs, key=lambda item: item[1], reverse=True) for facet, pairs in harvested.items()}
        for facet, pairs in ranked.items():
            for value, count in pairs:
                new_facet_values.append(
                    FacetValue(
                        catalogue_id=self.catalogue_id,
                        version_id=new_version.version_id,
                        facet=FacetId.from_str(facet),
                        value=value,
                        count=count,
                    )
                )
        store.update_facet_values(self.catalogue_id, new_facet_values)

        for facet_id in FacetId:
            facet_exposure = next(
                (fe for fe in self.facet_exposures if fe.facet == facet_id),
                FacetExposure(facet=facet_id),
            )
            new_version.facet_exposures.append(facet_exposure)
            pairs = ranked.get(facet_id.name)
            if pairs:
                facet_exposure.values_count = len(pairs)
                facet_exposure.total_count = sum(count for _, count in pairs)

        new_version.total_resources = sum(
            facet_exposure.total_count or 0 for facet_exposure in new_version.facet_exposures
        )
        return new_version

    def _add_error_version(self, e: Exception):
        new_version = self._create_catalogue_version()
        new_version.harvest_status = HarvestStatus.error
        new_version.harvest_error = str(e)

    async def apply(self) -> None:
        logger.info(f"Start apply for {self.catalogue_id}")
        start = datetime.now()
        try:
            clear_computed_ao_cat()
            harvested = self.harvest()
            _report(self.catalogue_id, harvested)
            new_version = self._add_version(harvested)
            await write_facet_values(new_version.catalogue_id, new_version.version_id)
        except Exception as e:
            logger.exception(f"Unexpected error during harvest: {e}")
            self._add_error_version(e)

        await update_catalogue_version()
        logger.info(f"End apply for {self.catalogue_id} in {datetime.now() - start}")
