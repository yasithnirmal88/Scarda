# Lazy imports — service classes are imported on demand to avoid
# circular imports caused by the model → database → migrations chain.
#
# Use: from app.services.dashboard_service import DashboardService (preferred)
#      from app.services import DashboardService (also works via __getattr__)

_MODULES: dict[str, type] = {}


def __getattr__(name: str):
    if name in _MODULES:
        return _MODULES[name]

    if name == "DashboardService":
        from app.services.dashboard_service import DashboardService as cls
    elif name == "StatisticsService":
        from app.services.statistics_service import StatisticsService as cls
    elif name == "NotificationService":
        from app.services.notification_service import NotificationService as cls
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    _MODULES[name] = cls
    return cls


__all__ = [
    "DashboardService",
    "StatisticsService",
    "NotificationService",
]