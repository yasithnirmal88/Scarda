from pydantic_settings import BaseSettings, SettingsConfigDict


class ThresholdConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="THRESHOLD_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    CURRENT_THRESHOLD_PCT: float = 30.0
    VOLTAGE_THRESHOLD_PCT: float = 15.0
    POWER_THRESHOLD_PCT: float = 30.0

    CONFIRMATION_CYCLES: int = 2
    MAX_CONFIRMATION_DELAY_MINUTES: int = 20

    SEVERITY_WARNING_THRESHOLD: float = 25.0
    SEVERITY_CRITICAL_THRESHOLD: float = 60.0

    ENABLE_RECOMMENDATIONS: bool = True

    OFFLINE_VOLTAGE_THRESHOLD: float = 10.0
    OFFLINE_CURRENT_THRESHOLD: float = 0.5

    COMMUNICATION_FAILURE_WINDOW_MINUTES: int = 30

    BASELINE_CURRENT: float = 10.0
    BASELINE_VOLTAGE: float = 820.0
    BASELINE_POWER: float = 8200.0