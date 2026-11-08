"""Sprint 5, user story 46: generate and store a daily report."""
from datetime import date

import pytest
from entity.reports.report import Report

pytestmark = [pytest.mark.sprint5, pytest.mark.story46]


def test_generate_daily_report_displays_and_saves_period_totals(app, manager_client, report_activity):
    response = manager_client.post('/manager/reports/daily', json=dict(startDate='2026-06-05'))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'daily', '2026-06-05', '2026-06-05')
    assert report['totals'] == dict(successfulLogins=1, newRegistrations=0, projectsCreated=1)
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'daily'
        assert (saved.start_date, saved.end_date) == (date.fromisoformat('2026-06-05'), date.fromisoformat('2026-06-05'))
        assert saved.totals == report['totals']
