from pydantic import BaseModel

from metacat_api.models.catalogue import Catalogue
from metacat_api.models.common import Collection
from metacat_api.models.facet import FacetExposure, FacetValue
from metacat_api.models.mapping import Mapping
from metacat_api.models.snapshot import Snapshot
from metacat_api.models.vocabulary import Concept, Vocabulary


class Store(BaseModel):
    catalogues: list[Catalogue]
    facet_values: list[FacetValue]
    facet_exposures: list[FacetExposure]
    vocabularies: list[Vocabulary]
    concepts: list[Concept]
    mappings: list[Mapping]
    snapshots: list[Snapshot]

    def get(self, collection: Collection) -> list[BaseModel]:
        match collection:
            case Collection.catalogues:
                return self.catalogues
            case Collection.facet_values:
                return self.facet_values
            case Collection.facet_exposures:
                return self.facet_exposures
            case Collection.vocabularies:
                return self.vocabularies
            case Collection.concepts:
                return self.concepts
            case Collection.mappings:
                return self.mappings
            case Collection.snapshots:
                return self.snapshots
            case _:
                raise ValueError(f"Unexcepted collection {collection}")
