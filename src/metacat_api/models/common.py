from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Collection(StrEnum):
    catalogues = "catalogues"
    catalogues_versions = "catalogues_versions"
    facet_values = "facet_values"
    vocabularies = "vocabularies"


COLLECTION_NAMES: dict[Collection, str] = {
    Collection.catalogues: "Catalogues",
    Collection.catalogues_versions: "Catalogues versions",
    Collection.facet_values: "Facet values",
    Collection.vocabularies: "Vocabularies",
}


CollectionValues = list[dict[str, Any]]


class Pagination(BaseModel):
    offset: int = Field(description="Index of the first returned item.")
    limit: int = Field(description="Maximum number of items returned.")
    total: int = Field(description="Total number of items available.")


class ErrorResponse(BaseModel):
    detail: str | None = Field(description="Human-readable error message.")
    code: str = Field(description="Machine-readable error code.")
