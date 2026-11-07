from calendar import monthrange
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from infrastructure.errors import DomainError


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


def validate_report_dates(kind, startDate, endDate=None):
    values, errors = {}, {}
    for name, raw in [('startDate',startDate), ('endDate',endDate)]:
        try:
            if name == 'endDate' and raw is None and kind in ('daily', 'weekly') and 'startDate' in values:
                value = values['startDate'] + timedelta(days=6 if kind == 'weekly' else 0)
            elif type(raw) is date:
                value = raw
            elif isinstance(raw, str):
                cleaned = raw.strip()
                value = date.fromisoformat(cleaned)
                if cleaned != value.isoformat():
                    raise ValueError()
            else:
                raise ValueError()
            if not 1900 <= value.year <= 9998:
                raise ValueError()
            values[name] = value
        except (ValueError, TypeError):
            errors[name] = ['Enter a valid date.']
    if errors:
        error = DomainError('Please correct the report dates.')
        error.field_errors = errors
        raise error
    start, end = values['startDate'], values['endDate']
    valid = start == end if kind == 'daily' else end-start == timedelta(days=6) if kind == 'weekly' else (
        start.day == 1 and end == start.replace(day=monthrange(start.year,start.month)[1]))
    if not valid:
        message = {'daily':'Choose one day for a daily report.', 'weekly':'Choose seven consecutive days for a weekly report.',
                   'monthly':'Choose the first and last day of one calendar month.'}[kind]
        error = DomainError(message)
        error.field_errors = {'endDate':[message]}
        raise error
    return start,end
