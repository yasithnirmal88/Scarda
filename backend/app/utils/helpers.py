from datetime import datetime


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.utcnow()
