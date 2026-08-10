from enum import StrEnum
from functools import cached_property, lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from pydantic import SecretBytes, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogFormat(StrEnum):
    json = "json"
    console = "console"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    json_data_dir: str

    log_level: str = "INFO"
    log_format: LogFormat = LogFormat.console

    api_keys: SecretStr

    git_username: SecretStr
    git_password: SecretStr

    @computed_field
    @cached_property
    def api_keys_bytes(self) -> list[SecretBytes]:
        return [
            SecretBytes(key.strip().encode("utf-8"))
            for key in self.api_keys.get_secret_value().split(",")
            if key.strip()
        ]

    def json_data_path(self) -> Path:
        return Path(self.json_data_dir).resolve()


settings = Settings()


@lru_cache
def get_version():
    try:
        return version(__package__)
    except PackageNotFoundError:
        return "0.0.0"
