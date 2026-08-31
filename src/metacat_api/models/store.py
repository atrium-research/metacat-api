import logging

from pydantic import BaseModel

from metacat_api.models.catalogue import Catalogue, CatalogueVersion
from metacat_api.models.facet import FacetValue
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
    facet_values: list[FacetValue] = []
    vocabularies: list[Vocabulary]

    def update(self, input_store: Store) -> None:
        tmp_store = input_store.model_copy(deep=True)
        self.catalogues = tmp_store.catalogues
        self.catalogues_versions = tmp_store.catalogues_versions
        self.facet_values = tmp_store.facet_values
        self.vocabularies = tmp_store.vocabularies

    def update_facet_values(self, catalogue_id: str, new_facet_values: list[FacetValue]) -> None:
        self.facet_values = [other_fv for other_fv in self.facet_values if other_fv.catalogue_id != catalogue_id]
        self.facet_values.extend([new_fv for new_fv in new_facet_values if new_fv.catalogue_id == catalogue_id])
