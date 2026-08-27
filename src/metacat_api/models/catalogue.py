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
    total_resources: int = Field(description="Total resources described by the catalogue.", default=0)
    harvest_at: datetime = Field(description="Timestamp of the harvest.")
    harvest_status: HarvestStatus = Field(description="Status of harvest.", default=HarvestStatus.success)
    harvest_error: str | None = Field(description="Reason of harvest error.", default=None)
    vocabularies: list[str] = Field(description="Used vocabularies.", default=[])
    facet_exposures: list[FacetExposure] = Field(description="Facet exposures.", default=[])
