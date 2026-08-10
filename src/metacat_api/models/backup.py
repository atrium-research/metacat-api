from pydantic import BaseModel


class DataFile(BaseModel):
    name: str
    size: int


class BackupInfo(BaseModel):
    last_update: str
    data_files: list[DataFile] = []
