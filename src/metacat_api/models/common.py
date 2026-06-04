from enum import StrEnum

from pydantic import BaseModel, Field


class PivotFacet(StrEnum):
    resource_type = "resource-type"
    format = "format"
    discipline = "discipline"
    source = "source"
    source_2 = "source-2"
    subjects = "subjects"


class FacetExposureStatus(StrEnum):
    exposed = "exposed"
    partial = "partial"
    implicit = "implicit"
    gap = "gap"


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
    detail: str = Field(description="Human-readable error message.")
    code: str = Field(description="Machine-readable error code.")
