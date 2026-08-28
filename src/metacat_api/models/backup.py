from functools import cached_property

from pydantic import BaseModel, computed_field

from metacat_api.services.util import sizeof_fmt


class DataFile(BaseModel):
    name: str
    filename: str
    size: int

    @computed_field
    @cached_property
    def size_human(self) -> str:
        return sizeof_fmt(self.size)


class BackupLastUpdate(BaseModel):
    last_update: str


class BackupInfo(BackupLastUpdate):
    data_files: list[DataFile] = []
