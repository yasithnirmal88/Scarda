"""WebSocket configuration settings.

Centralizes all WebSocket-related timeout and heartbeat values
to avoid hardcoded magic numbers across the codebase.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class WebSocketConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WS_", env_file=".env", env_file_encoding="utf-8", extra="ignore")

    HEARTBEAT_INTERVAL: int = 30
    STALE_TIMEOUT: float = 60.0
