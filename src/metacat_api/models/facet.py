from datetime import datetime

from pydantic import BaseModel, Field

from metacat_api.models.common import FacetExposureStatus, FacetId


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
    facet: FacetId = Field(description="Facet the value belongs to.")
    value: str = Field(description="Facet value label.")
    count: int = Field(description="Number of resources carrying this value.")
    timestamp: datetime = Field(description="Version timestamp of the count.")


class FacetTimeseriesPoint(BaseModel):
    catalogue_id: str = Field(description="Catalogue the point belongs to.")
    facet: FacetId = Field(description="Facet the point belongs to.")
    timestamp: datetime = Field(description="Timestamp of the version.")
    total_count: int = Field(description="Total count for the facet at this timestamp.")


class FacetComparisonRow(BaseModel):
    value: str = Field(description="Facet value compared across catalogues.")
    counts: dict[str, int | None] = Field(
        description="Per-catalogue count, null means the facet is a gap for that catalogue."
    )


class FacetComparison(BaseModel):
    facet: FacetId = Field(description="Facet being compared.")
    catalogues: list[str] = Field(description="Catalogues included in the comparison.")
    values: list[FacetComparisonRow] = Field(description="One row per distinct facet value.")
