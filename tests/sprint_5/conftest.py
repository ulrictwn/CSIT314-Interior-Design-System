"""Known activity inside June 2026, plus an event outside every report period."""
from datetime import datetime, timezone

import pytest
from entity.reports.activity_event import ActivityEvent
from infrastructure.database import db


@pytest.fixture
def report_activity(app):
    with app.app_context():
        db.session.add_all([
            ActivityEvent(kind='login_success', occurred_at=datetime(2026, 6, 5, 1, tzinfo=timezone.utc)),
            ActivityEvent(kind='project_new_created', occurred_at=datetime(2026, 6, 5, 2, tzinfo=timezone.utc)),
            ActivityEvent(kind='login_success', occurred_at=datetime(2026, 7, 3, 1, tzinfo=timezone.utc)),
        ])
        db.session.commit()
