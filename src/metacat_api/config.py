from enum import StrEnum
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Datasource(StrEnum):
    mock = "mock"
    json = "json"
    sparql = "sparql"


class LogFormat(StrEnum):
    json = "json"
    console = "console"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    datasource: Datasource = Datasource.mock
    json_data_dir: str = "./data"
    mock_data_dir: str = "./src/metacat_api/mock_data"
    sparql_endpoint: str = ""
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.console

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
