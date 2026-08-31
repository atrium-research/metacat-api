from enum import StrEnum
from typing import Any


class Collection(StrEnum):
    catalogues = "catalogues"
    catalogues_versions = "catalogues_versions"
    facet_values = "facet_values"
    vocabularies = "vocabularies"


COLLECTION_LABELS: dict[Collection, str] = {
    Collection.catalogues: "Catalogues",
    Collection.catalogues_versions: "Catalogues versions",
    Collection.facet_values: "Facet values",
    Collection.vocabularies: "Vocabularies",
}


CollectionValues = list[dict[str, Any]]
