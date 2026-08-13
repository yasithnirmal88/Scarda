from pydantic_settings import BaseSettings, SettingsConfigDict


class HuaweiConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HUAWEI_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    BASE_URL: str = "http://127.0.0.1:8000"
    USERNAME: str = "huawei"
    PASSWORD: str = "huawei"
    PLANT_ID: str = "sim-plant-001"
    TIMEOUT_SECONDS: float = 10.0
    LOGIN_PATH: str = "/api/auth/login"
    PLANTS_PATH: str = "/api/plants"