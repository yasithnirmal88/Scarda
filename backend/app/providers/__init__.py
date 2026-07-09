from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.providers.interfaces import IDataProvider


def create_provider() -> IDataProvider:
    """Factory: returns the configured data provider.

    The provider type is read from ``settings.PROVIDER_TYPE``:
    - ``"fake"``      → ``FakeProvider`` (default, hardcoded data)
    - ``"simulator"`` → ``SimulatorProvider`` (stateful solar-farm simulator)
    - ``"huawei"``    → ``HuaweiProvider`` (placeholder — not implemented)

    No service should call any concrete provider class directly.
    """
    provider_type = settings.PROVIDER_TYPE

    if provider_type == "simulator":
        from app.providers.simulator import SimulatorProvider

        return SimulatorProvider()
    elif provider_type == "huawei":
        from app.providers.huawei import HuaweiProvider

        return HuaweiProvider()

    from app.providers.fake import FakeProvider

    return FakeProvider()
