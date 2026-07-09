from app.config.settings import AppSettings, get_settings

settings = get_settings()

__all__ = ["settings", "AppSettings", "get_settings"]