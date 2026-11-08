"""Sprint 5, user story 47: generate and store a weekly report."""
from datetime import date

import pytest
from entity.reports.report import Report

pytestmark = [pytest.mark.sprint5, pytest.mark.story47]


def test_generate_weekly_report_displays_and_saves_period_totals(app, manager_client, report_activity):
    response = manager_client.post('/manager/reports/weekly', json=dict(startDate='2026-06-01'))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'weekly', '2026-06-01', '2026-06-07')
    assert report['totals'] == dict(successfulLogins=1, newRegistrations=0, projectsCreated=1)
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'weekly'
        assert (saved.start_date, saved.end_date) == (date.fromisoformat('2026-06-01'), date.fromisoformat('2026-06-07'))
        assert saved.totals == report['totals']
