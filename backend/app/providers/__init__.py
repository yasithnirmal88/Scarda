from __future__ import annotations

from typing import Any

from app.config import settings
from app.providers.interfaces import IDataProvider


def create_provider() -> IDataProvider:
    """Factory: returns the configured data provider.

    The provider type is read from ``settings.PROVIDER_TYPE``:
    - ``"huawei"`` → ``HuaweiProvider`` (default). Talks to the
      mock-fusionsolar API in development and the real Huawei FusionSolar
      Northbound API in production. This is the only data source Scarda uses;
      simulated data MUST come from the separate mock-fusionsolar project,
      never from inside Scarda.

    No service should call any concrete provider class directly. Scarda never
    generates fake data itself; when no provider is reachable the app degrades
    gracefully (empty readings, health=degraded) rather than fabricating data.
    """
    provider_type = settings.PROVIDER_TYPE

    if provider_type == "huawei":
        from app.providers.huawei import HuaweiProvider

        return HuaweiProvider()

    # Unknown provider type → fail loudly rather than silently fabricating data.
    raise RuntimeError(
        f"Unknown PROVIDER_TYPE={provider_type!r}. Supported: 'huawei'. "
        "Scarda does not generate data internally; point HUAWEI_BASE_URL at the "
        "mock-fusionsolar API (dev) or the real Huawei API (prod)."
    )
