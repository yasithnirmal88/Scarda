from pydantic_settings import BaseSettings, SettingsConfigDict


class SchedulerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SCHEDULER_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENABLED: bool = True
    SIMULATOR_INTERVAL_MINUTES: int = 10
    ALERT_INTERVAL_MINUTES: int = 10
    CLEANUP_INTERVAL_HOURS: int = 24
    STATS_INTERVAL_MINUTES: int = 15