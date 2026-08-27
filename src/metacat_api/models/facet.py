from uuid import UUID

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
    version_id: UUID = Field(description="Catalogue version the value belongs to.")
    facet: FacetId = Field(description="Facet the value belongs to.")
    value: str = Field(description="Facet value label.")
    count: int = Field(description="Number of resources carrying this value.")
