from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    id: str
    name: str
    next_run_time: datetime
    trigger: str
