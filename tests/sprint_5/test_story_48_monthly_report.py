"""Sprint 5, user story 48: generate and store a monthly report."""
from datetime import date

import pytest
from entity.reports.report import Report

pytestmark = [pytest.mark.sprint5, pytest.mark.story48]


def test_generate_monthly_report_displays_and_saves_period_totals(app, client, report_activity):
    response = client.post('/manager/reports/monthly', json=dict(startDate='2026-06-01', endDate='2026-06-30'))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'monthly', '2026-06-01', '2026-06-30')
    assert report['totals'] == dict(successfulLogins=1, newRegistrations=0, projectsCreated=1)
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'monthly'
        assert (saved.start_date, saved.end_date) == (date.fromisoformat('2026-06-01'), date.fromisoformat('2026-06-30'))
        assert saved.totals == report['totals']
