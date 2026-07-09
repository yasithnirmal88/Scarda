from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOGGING_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    LEVEL: str = "INFO"
    FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    UVICORN_ACCESS_LEVEL: str = "WARNING"