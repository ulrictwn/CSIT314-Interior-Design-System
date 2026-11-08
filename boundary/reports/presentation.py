from calendar import monthrange
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def default_dates(kind):
    today = datetime.now(ZoneInfo('Asia/Singapore')).date()
    if kind == 'daily':
        start = end = today-timedelta(days=1)
    elif kind == 'weekly':
        end = today-timedelta(days=today.weekday()+1)
        start = end-timedelta(days=6)
    else:
        end = today.replace(day=1)-timedelta(days=1)
        start = end.replace(day=1)
    return dict(startDate=start.isoformat(), endDate=end.isoformat())


