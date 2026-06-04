from datetime import datetime

from pydantic import BaseModel, Field


class Snapshot(BaseModel):
    id: str = Field(description="Stable identifier of the snapshot.")
    taken_at: datetime = Field(description="Timestamp the snapshot was taken.")
    catalogues_included: list[str] = Field(
        description="Catalogue identifiers covered by the snapshot."
    )
