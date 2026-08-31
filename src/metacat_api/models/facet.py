from enum import StrEnum, auto
from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel, Field, TypeAdapter


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


class FacetExposure(BaseModel):
    facet: FacetId = Field(description="The facet identifier.")
    status: FacetExposureStatus = Field(
        default=FacetExposureStatus.exposed,
        description="How the catalogue exposes this facet.",
    )
    reason: str | None = Field(default=None, description="Explanation when the facet is a gap, or implicit.")
    values_count: int | None = Field(default=None, description="Number of distinct values, null when not exposed.")
    total_count: int | None = Field(default=None, description="Sum of counts across all values of the facet.")


class FacetValue(BaseModel):
    catalogue_id: str = Field(description="Catalogue the value belongs to.")
    version_id: UUID = Field(description="Catalogue version the value belongs to.")
    facet: FacetId = Field(description="Facet the value belongs to.")
    value: str = Field(description="Facet value label.")
    count: int = Field(description="Number of resources carrying this value.")


class FacetValuesSort(StrEnum):
    facet = auto()
    value = auto()
    count = auto()


class FacetValuesSortDirection(StrEnum):
    asc = auto()
    desc = auto()
