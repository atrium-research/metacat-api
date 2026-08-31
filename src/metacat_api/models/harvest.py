from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    name: str
    next_run_time: datetime | None = None
    trigger: str


class HarvestStatus(StrEnum):
    success = "success"
    error = "error"
