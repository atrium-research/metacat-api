from enum import StrEnum, auto
from typing import Any, TypedDict

from pydantic import BaseModel, Field, TypeAdapter


class Collection(StrEnum):
    catalogues = "catalogues"
    catalogues_versions = "catalogues_versions"
    facet_values = "facet_values"
    vocabularies = "vocabularies"


COLLECTION_NAMES: dict[Collection, str] = {
    Collection.catalogues: "Catalogues",
    Collection.catalogues_versions: "Catalogues versions",
    Collection.facet_values: "Facet values",
    Collection.vocabularies: "Vocabularies",
}


CollectionValues = list[dict[str, Any]]


class FacetId(StrEnum):
    resource_type = "resource-type"
    format = auto()
    discipline = auto()
    source = auto()
    source_2 = "source-2"
    subjects = auto()

    @staticmethod
    def from_str(label):
        match label:
            case "resource_type":
                return FacetId.resource_type
            case "source_2":
                return FacetId.source_2
            case x:
                return FacetId(x)


RawFacetValue = tuple[str, int]
RawFacetValues = list[RawFacetValue]


class RawFacets(TypedDict, total=False):
    resource_type: RawFacetValues
    format: RawFacetValues
    discipline: RawFacetValues
    source: RawFacetValues
    source_2: RawFacetValues
    subjects: RawFacetValues


raw_facets_adapter = TypeAdapter(RawFacets)


class FacetExposureStatus(StrEnum):
    exposed = "exposed"
    implicit = "implicit"
    gap = "gap"


class HarvestStatus(StrEnum):
    success = "success"
    error = "error"


class Pagination(BaseModel):
    offset: int = Field(description="Index of the first returned item.")
    limit: int = Field(description="Maximum number of items returned.")
    total: int = Field(description="Total number of items available.")


class ErrorResponse(BaseModel):
    detail: str | None = Field(description="Human-readable error message.")
    code: str = Field(description="Machine-readable error code.")
