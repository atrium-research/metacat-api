from enum import StrEnum
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class LogFormat(StrEnum):
    json = "json"
    console = "console"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    json_data_dir: str

    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.console

    api_keys: Annotated[list[bytes], NoDecode]

    @field_validator("api_keys", mode="before")
    @classmethod
    def split_api_keys(cls, keys: str) -> list[bytes]:
        return [key.strip().encode("utf-8") for key in keys.split(",") if key.strip()]

    def json_data_path(self) -> Path:
        return Path(self.json_data_dir).resolve()


settings = Settings()


@lru_cache
def get_version():
    try:
        return version(__package__)
    except PackageNotFoundError:
        return "0.0.0"
