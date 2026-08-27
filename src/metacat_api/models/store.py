import logging
from collections import defaultdict
from functools import cached_property

from pydantic import BaseModel, computed_field

from metacat_api.models.catalogue import Catalogue, CatalogueVersion
from metacat_api.models.common import Collection
from metacat_api.models.facet import FacetExposure, FacetTimeseriesPoint, FacetValue
from metacat_api.models.vocabulary import Vocabulary

logger = logging.getLogger(__name__)


class Store(BaseModel):
    """Reads timestamped JSON from the metacat-data store.

    Expects a directory holding the metacat-data layout (one file per
    collection). Missing files are treated as empty collections so a
    partially populated store still serves. The store is produced by the
    harvesting connectors in metacat-code (see src/metacat_api/harvesters/clarin.py).
    """

    catalogues: list[Catalogue]
    catalogues_versions: list[CatalogueVersion]
    facet_values: list[FacetValue]
    facet_exposures: list[FacetExposure]
    vocabularies: list[Vocabulary]

    @computed_field
    @cached_property
    def catalogue_ids(self) -> list[str]:
        return [c.id for c in self.catalogues]

    @computed_field
    def facet_timeseries(self) -> list[FacetTimeseriesPoint]:
        totals: dict[tuple, int] = defaultdict(int)
        for value in self.facet_values:
            totals[(value.catalogue_id, value.facet, value.timestamp)] += value.count
        points = [
            FacetTimeseriesPoint(
                catalogue_id=catalogue_id,
                facet=facet,
                timestamp=timestamp,
                total_count=total,
            )
            for (catalogue_id, facet, timestamp), total in totals.items()
        ]
        points.sort(key=lambda point: (point.catalogue_id, point.facet.value, point.timestamp))
        return points

    def get(self, collection: Collection) -> list[BaseModel]:
        match collection:
            case Collection.catalogues:
                return self.catalogues
            case Collection.catalogues_versions:
                return self.catalogues_versions
            case Collection.facet_values:
                return self.facet_values
            case Collection.facet_exposures:
                return self.facet_exposures
            case Collection.vocabularies:
                return self.vocabularies
            case _:
                raise ValueError(f"Unexcepted collection {collection}")

    def update(self, input_store: Store) -> None:
        tmp_store = input_store.model_copy(deep=True)
        self.catalogues = tmp_store.catalogues
        self.catalogues_versions = tmp_store.catalogues_versions
        self.facet_values = tmp_store.facet_values
        self.facet_exposures = tmp_store.facet_exposures
        self.vocabularies = tmp_store.vocabularies
