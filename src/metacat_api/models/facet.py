from datetime import datetime

from pydantic import BaseModel, Field

from metacat_api.models.common import FacetExposureStatus, PivotFacet
from metacat_api.models.vocabulary import ConceptRef


class FacetExposure(BaseModel):
    catalogue_id: str = Field(description="Catalogue the exposure refers to.")
    facet: PivotFacet = Field(description="Pivot facet being described.")
    status: FacetExposureStatus = Field(description="How the catalogue exposes this facet.")
    reason: str | None = Field(default=None, description="Explanation when the facet is a gap, implicit or partial.")
    values_count: int | None = Field(default=None, description="Number of distinct values, null when not exposed.")
    top_value: str | None = Field(default=None, description="Most frequent value, null when not exposed.")
    top_value_count: int | None = Field(default=None, description="Count of the most frequent value.")
    total_count: int | None = Field(default=None, description="Sum of counts across all values of the facet.")


class FacetValue(BaseModel):
    catalogue_id: str = Field(description="Catalogue the value belongs to.")
    facet: PivotFacet = Field(description="Pivot facet the value belongs to.")
    value: str = Field(description="Facet value label.")
    count: int = Field(description="Number of resources carrying this value.")
    timestamp: datetime = Field(description="Snapshot timestamp of the count.")
    vocabulary_term: ConceptRef | None = Field(
        default=None, description="Controlled vocabulary term backing the value, if any."
    )


class FacetTimeseriesPoint(BaseModel):
    catalogue_id: str = Field(description="Catalogue the point belongs to.")
    facet: PivotFacet = Field(description="Pivot facet the point belongs to.")
    timestamp: datetime = Field(description="Timestamp of the snapshot.")
    total_count: int = Field(description="Total count for the facet at this timestamp.")


class FacetComparisonRow(BaseModel):
    value: str = Field(description="Facet value compared across catalogues.")
    counts: dict[str, int | None] = Field(
        description="Per-catalogue count, null means the facet is a gap for that catalogue."
    )


class FacetComparison(BaseModel):
    facet: PivotFacet = Field(description="Pivot facet being compared.")
    catalogues: list[str] = Field(description="Catalogues included in the comparison.")
    snapshot_timestamp: datetime = Field(description="Snapshot the comparison is based on.")
    values: list[FacetComparisonRow] = Field(description="One row per distinct facet value.")
