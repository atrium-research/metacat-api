from enum import StrEnum, auto
from typing import Any, TypedDict

from pydantic import BaseModel, Field, TypeAdapter


class Collection(StrEnum):
    catalogues = "catalogues"
    facet_values = "facet_values"
    facet_exposures = "facet_exposures"
    vocabularies = "vocabularies"
    concepts = "concepts"
    mappings = "mappings"
    snapshots = "snapshots"


CollectionValues = list[dict[str, Any]]


class PivotFacet(StrEnum):
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
                return PivotFacet.resource_type
            case "source_2":
                return PivotFacet.source_2
            case x:
                return PivotFacet(x)


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


Reasons = dict[PivotFacet, str]


class FacetExposureStatus(StrEnum):
    exposed = "exposed"
    partial = "partial"
    implicit = "implicit"
    gap = "gap"


StatusOverrides = dict[PivotFacet, FacetExposureStatus]


class MappingRelation(StrEnum):
    exactMatch = "exactMatch"
    closeMatch = "closeMatch"
    broadMatch = "broadMatch"
    narrowMatch = "narrowMatch"
    relatedMatch = "relatedMatch"


class HarvestStatus(StrEnum):
    live = "live"
    degraded = "degraded"
    unreachable = "unreachable"


class Pagination(BaseModel):
    offset: int = Field(description="Index of the first returned item.")
    limit: int = Field(description="Maximum number of items returned.")
    total: int = Field(description="Total number of items available.")


class ErrorResponse(BaseModel):
    detail: str | None = Field(description="Human-readable error message.")
    code: str = Field(description="Machine-readable error code.")
