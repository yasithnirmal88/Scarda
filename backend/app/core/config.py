from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Solar AIM"
    DEBUG: bool = False
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/solar_aim"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SCHEDULER_ENABLED: bool = True
    SCHEDULER_SIMULATOR_INTERVAL_MINUTES: int = 10
    SCHEDULER_ALERT_INTERVAL_MINUTES: int = 10
    SCHEDULER_CLEANUP_INTERVAL_HOURS: int = 24
    SCHEDULER_STATS_INTERVAL_MINUTES: int = 15

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
