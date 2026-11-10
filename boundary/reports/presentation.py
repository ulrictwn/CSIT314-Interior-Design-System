from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def default_dates(kind):
    """Choose the initial dates shown on the selected report form."""
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


def report_metrics(report):
    """Return display labels for current or older saved report totals."""
    if 'topCategory' in report.totals:
        return [
            ('New IDPs created', 'projectsCreated', 'New projects created in this period'),
            ('Customer shortlists', 'shortlistSaves', 'Times customers saved a project in this period'),
            ('Top IDP category', 'topCategory', 'Category with the most new IDPs'),
        ]
    # Existing saved reports remain readable in their original format.
    return [
        ('Successful logins', 'successfulLogins', 'Across all platform roles'),
        ('New registrations', 'newRegistrations', 'Accounts created in this period'),
        ('Projects created', 'projectsCreated', 'New and past design projects added'),
    ]
