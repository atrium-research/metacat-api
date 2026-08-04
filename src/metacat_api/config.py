from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


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
