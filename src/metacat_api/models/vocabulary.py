from pydantic import BaseModel, Field, HttpUrl

from metacat_api.models.common import PivotFacet


class ConceptRef(BaseModel):
    uri: HttpUrl = Field(description="Stable URI identifying the concept.")
    pref_label: str = Field(description="Preferred label of the concept.")
    scheme: str = Field(description="Concept scheme or authority the term belongs to.")


class Concept(BaseModel):
    uri: HttpUrl = Field(description="Stable URI identifying the concept.")
    pref_label: str = Field(description="Preferred label of the concept.")
    scheme: str = Field(description="Concept scheme the term belongs to.")
    vocabulary_id: str = Field(description="Identifier of the owning vocabulary.")


class Vocabulary(BaseModel):
    id: str = Field(description="Stable identifier of the vocabulary.")
    name: str = Field(description="Display name of the vocabulary.")
    authority: str = Field(description="Organisation maintaining the vocabulary.")
    uri: HttpUrl | None = Field(default=None, description="Canonical URI of the vocabulary.")
    concepts_count: int = Field(description="Number of concepts in the vocabulary.")
    used_for_facets: list[PivotFacet] = Field(description="Pivot facets this vocabulary provides terms for.")
    used_by_catalogues: list[str] = Field(description="Catalogue identifiers using this vocabulary.")
