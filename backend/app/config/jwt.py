from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="JWT_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30