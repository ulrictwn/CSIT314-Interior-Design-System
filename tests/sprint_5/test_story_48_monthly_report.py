"""Sprint 5, user story 48: report one month's new IDPs, shortlist saves and top category."""
from datetime import date, datetime, timezone

import pytest
from unittest.mock import Mock
from entity.projects.interior_design_project import InteriorDesignProject
from entity.reports.activity_event import ActivityEvent
from entity.reports.report import Report
from infrastructure.database import db

pytestmark = [pytest.mark.sprint5, pytest.mark.story48]


def test_TC65_generate_monthly_report_displays_and_saves_period_totals(app, manager_client, report_activity, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.reports.monthly_report_page.MonthlyReportController.generateMonthlyReport', blocked)
        invalid = manager_client.post('/manager/reports/monthly', json={'startDate': '2026-06-15', 'endDate': '2026-06-30'})
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = manager_client.post('/manager/reports/monthly', json=dict(startDate='2026-06-01', endDate='2026-06-30'))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'monthly', '2026-06-01', '2026-06-30')
    assert report['totals'] == report_activity['totals']
    assert report['rows'] == report_activity['rows']
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'monthly'
        assert (saved.start_date, saved.end_date) == (date(2026, 6, 1), date(2026, 6, 30))
        assert saved.totals == report['totals']
        # The final instant of June in Singapore counts; 1 July does not.
        project = InteriorDesignProject()
        assert project.createNewProject(report_activity['designer'], 'June End Home', report_activity['japandi_id'],
            'Apartment', 'Bedok', 80000, 'Created at the end of the month.')
        event = db.session.scalar(db.select(ActivityEvent).where(ActivityEvent.kind == 'project_new_created',
            ActivityEvent.target_id == str(project.project_id)))
        event.occurred_at = datetime(2026, 6, 30, 15, 59, 59, 999999, tzinfo=timezone.utc)
        db.session.commit()
    tied = manager_client.post('/manager/reports/monthly', json=dict(startDate='2026-06-01', endDate='2026-06-30'))
    assert tied.status_code == 201
    # Equal counts use alphabetical category-name order, making the result stable.
    assert tied.json['report']['totals'] == dict(projectsCreated=4, shortlistSaves=3, topCategory='Japandi')
    assert tied.json['report']['rows'] == [dict(area='IDP categories', activity='Japandi', total=2),
                                         dict(area='IDP categories', activity='Scandinavian', total=2)]
