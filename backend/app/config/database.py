from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/solar_aim"