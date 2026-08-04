from enum import StrEnum
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class LogFormat(StrEnum):
    json = "json"
    console = "console"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    json_data_dir: str

    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.console

    admin_password: str


settings = Settings()
