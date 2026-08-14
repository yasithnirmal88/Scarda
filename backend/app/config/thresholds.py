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

    # Weather-aware physics-model baseline (Tier 1).
    # Expected output scales with irradiance and temperature rather than
    # being a fixed constant, so a cloud/night drop in generation is not
    # mistaken for a fault.
    STC_IRRADIANCE_WPM2: float = 1000.0          # Standard Test Conditions irradiance
    TEMP_COEFFICIENT_PCT: float = -0.4            # %/C, power drops ~0.4% per C above 25
    RATED_POWER_PER_STRING_W: float = 250.0     # String nameplate at STC
    RATED_VOLTAGE_V: float = 820.0              # nominal string voltage (weather-insensitive)
    RATED_CURRENT_A: float = 10.0               # nominal string current at STC
    NIGHT_IRRADIANCE_WPM2: float = 20.0         # below this -> treat as night, no output expected