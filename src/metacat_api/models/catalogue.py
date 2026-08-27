from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from metacat_api.models.common import HarvestStatus
from metacat_api.models.facet import FacetExposure

CatalogueId = str
VersionId = UUID


class Catalogue(BaseModel):
    id: CatalogueId = Field(description="Stable identifier, lowercase and hyphen-separated.")
    name: str = Field(description="Display name of the catalogue.")
    domain: str = Field(description="Primary domain covered by the catalogue.")
    url: HttpUrl = Field(description="Public entry point of the catalogue.")
    licence: str = Field(description="Licence under which the catalogue exposes its metadata.")
    languages_summary: str = Field(description="Short summary of the languages present in the catalogue.")


class CatalogueVersion(BaseModel):
    catalogue_id: CatalogueId = Field(description="Stable identifier, lowercase and hyphen-separated.")
    version_id: VersionId = Field(description="Version identifier.")
    total_resources: int | None = Field(description="Total resources described by the catalogue.", default=None)
    harvest_at: datetime | None = Field(description="Timestamp of the harvest.", default=None)
    harvest_status: HarvestStatus | None = Field(description="Status of harvest.", default=None)
    vocabularies: list[str] = Field(description="Used vocabularies.", default=[])
    facets: list[FacetExposure] = Field(description="Facet exposures.", default=[])
