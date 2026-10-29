from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import current_app


def utcnow():
    return datetime.now(timezone.utc)


def local_today():
    return datetime.now(ZoneInfo(current_app.config['APP_TIMEZONE'])).date()
