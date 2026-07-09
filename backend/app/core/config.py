"""Legacy re-export — prefer ``from app.config import settings``."""

from app.config import settings as _settings
from app.config.settings import AppSettings, get_settings

settings = _settings

__all__ = ["settings", "AppSettings", "get_settings"]