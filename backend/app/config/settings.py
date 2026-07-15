"""Application settings singleton.

Composes all sub-configuration objects and provides a single
get_settings() accessor for the entire application.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.database import DatabaseConfig
from app.config.jwt import JWTConfig
from app.config.scheduler import SchedulerConfig
from app.config.thresholds import ThresholdConfig
from app.config.logging import LoggingConfig
from app.config.websocket import WebSocketConfig


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

    APP_NAME: str = "Solar AIM"
    DEBUG: bool = False
    PROVIDER_TYPE: str = "fake"

    database: DatabaseConfig = DatabaseConfig()
    jwt: JWTConfig = JWTConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    thresholds: ThresholdConfig = ThresholdConfig()
    logging: LoggingConfig = LoggingConfig()
    websocket: WebSocketConfig = WebSocketConfig()


_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings
