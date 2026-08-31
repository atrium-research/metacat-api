from pydantic import BaseModel, Field


class Pagination(BaseModel):
    offset: int = Field(description="Index of the first returned item.")
    limit: int = Field(description="Maximum number of items returned.")
    total: int = Field(description="Total number of items available.")


class ErrorResponse(BaseModel):
    detail: str | None = Field(description="Human-readable error message.")
    code: str = Field(description="Machine-readable error code.")
