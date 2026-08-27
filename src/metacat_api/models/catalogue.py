from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from metacat_api.models.common import HarvestStatus


class StaticCatalogue(BaseModel):
    id: str = Field(description="Stable identifier, lowercase and hyphen-separated.")
    name: str = Field(description="Display name of the catalogue.")
    domain: str = Field(description="Primary domain covered by the catalogue.")
    url: HttpUrl = Field(description="Public entry point of the catalogue.")
    licence: str = Field(description="Licence under which the catalogue exposes its metadata.")
    languages_summary: str = Field(description="Short summary of the languages present in the catalogue.")


class Catalogue(StaticCatalogue):
    total_resources: int | None = Field(description="Total resources described by the catalogue.", default=None)
    last_harvest_at: datetime | None = Field(description="Timestamp of the last successful harvest.", default=None)
    harvest_status: HarvestStatus | None = Field(description="Status of the most recent harvest.", default=None)
