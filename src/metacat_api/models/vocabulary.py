from pydantic import BaseModel, Field, HttpUrl


class Vocabulary(BaseModel):
    id: str = Field(description="Stable identifier of the vocabulary.")
    name: str = Field(description="Display name of the vocabulary.")
    authority: str = Field(description="Organisation maintaining the vocabulary.")
    uri: HttpUrl | None = Field(default=None, description="Canonical URI of the vocabulary.")
