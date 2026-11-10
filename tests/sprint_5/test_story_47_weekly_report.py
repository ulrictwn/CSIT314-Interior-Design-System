"""Sprint 5, user story 47: store a weekly snapshot of IDP and shortlist activity."""
from datetime import date, datetime, timezone

import pytest
from unittest.mock import Mock
from entity.reports.activity_event import ActivityEvent
from entity.reports.report import Report
from infrastructure.database import db

pytestmark = [pytest.mark.sprint5, pytest.mark.story47]


def test_TC64_generate_weekly_report_displays_and_saves_period_totals(app, manager_client, report_activity, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.reports.weekly_report_page.WeeklyReportController.generateWeeklyReport', blocked)
        invalid = manager_client.post('/manager/reports/weekly', json={'startDate': '2026-06-01', 'endDate': '2026-06-01'})
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = manager_client.post('/manager/reports/weekly', json=dict(startDate='2026-06-01'))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'weekly', '2026-06-01', '2026-06-07')
    assert report['totals'] == report_activity['totals']
    assert report['rows'] == report_activity['rows']
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'weekly'
        assert (saved.start_date, saved.end_date) == (date(2026, 6, 1), date(2026, 6, 7))
        assert saved.totals == report['totals']
        # Later activity does not change a saved report or its download.
        db.session.add(ActivityEvent(kind='shortlist_saved', occurred_at=datetime(2026, 6, 5, 3, tzinfo=timezone.utc)))
        legacy = Report(report_type='weekly', start_date=date(2026, 5, 1), end_date=date(2026, 5, 7),
            totals=dict(successfulLogins=2, newRegistrations=1, projectsCreated=4),
            rows=[dict(area='Customer activity', activity='Project views', total=5)])
        db.session.add(legacy)
        db.session.commit()
        legacy_id = legacy.report_id
    snapshot = manager_client.get('/manager/reports/' + str(report['reportId']))
    assert snapshot.status_code == 200
    assert snapshot.json['report']['totals'] == report['totals']
    refreshed = manager_client.post('/manager/reports/weekly', json=dict(startDate='2026-06-01'))
    assert refreshed.json['report']['totals'] == dict(report_activity['totals'], shortlistSaves=4)
    for suffix in ('', '/download'):
        legacy_page = manager_client.get('/manager/reports/' + str(legacy_id) + suffix,
                                         headers={'Accept': 'text/html'})
        assert legacy_page.status_code == 200
        assert b'Successful logins' in legacy_page.data
