from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from metacat_api.models.common import HarvestStatus


class Catalogue(BaseModel):
    id: str = Field(description="Stable identifier, lowercase and hyphen-separated.")
    name: str = Field(description="Display name of the catalogue.")
    domain: str = Field(description="Primary domain covered by the catalogue.")
    url: HttpUrl = Field(description="Public entry point of the catalogue.")
    total_resources: int = Field(description="Total resources described by the catalogue.")
    vocabularies_count: int = Field(description="Number of vocabularies used by the catalogue.")
    vocabularies_mapped: int = Field(description="Number of used vocabularies with declared cross-mappings.")
    licence: str = Field(description="Licence under which the catalogue exposes its metadata.")
    last_harvest_at: datetime = Field(description="Timestamp of the last successful harvest.")
    harvest_status: HarvestStatus = Field(description="Status of the most recent harvest.")
    languages_summary: str | None = Field(
        default=None, description="Short summary of the languages present in the catalogue."
    )
