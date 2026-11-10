from datetime import datetime, timezone


def utcnow():
    """Return a UTC timestamp for model defaults and recorded activity."""
    return datetime.now(timezone.utc)
