from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Collection(StrEnum):
    catalogues = "catalogues"
    facet_values = "facet_values"
    facet_exposures = "facet_exposures"
    vocabularies = "vocabularies"
    concepts = "concepts"
    mappings = "mappings"
    snapshots = "snapshots"


COLLECTIONS = [collection.value for collection in Collection]


CollectionValues = list[dict[str, Any]]


class PivotFacet(StrEnum):
    resource_type = "resource-type"
    format = "format"
    discipline = "discipline"
    source = "source"
    source_2 = "source-2"
    subjects = "subjects"


FACETS = [facet.value for facet in PivotFacet]

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
