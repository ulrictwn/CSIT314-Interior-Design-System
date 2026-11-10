"""Sprint 5, user story 48: report one month's new IDPs, shortlist saves and top category."""
from datetime import date, datetime, timezone

import pytest
from entity.projects.interior_design_project import InteriorDesignProject
from entity.reports.activity_event import ActivityEvent
from entity.reports.report import Report
from infrastructure.database import db

pytestmark = [pytest.mark.sprint5, pytest.mark.story48]


def test_TC65_generate_monthly_report_displays_and_saves_period_totals(app, manager_client, report_activity):
    # Invalid input passes through the controller and is rejected by the entity.
    invalid = manager_client.post('/manager/reports/monthly', json={'startDate': '2026-06-30', 'endDate': '2026-06-01'})
    assert invalid.status_code == 400
    assert 'endDate' in invalid.json['errors']
    with app.app_context():
        assert Report.query.count() == 0
    response = manager_client.post('/manager/reports/monthly', json=dict(startDate='2026-06-01', endDate='2026-06-30'))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'monthly', '2026-06-01', '2026-06-30')
    assert report['totals'] == report_activity['monthly']['totals']
    assert report['rows'] == report_activity['monthly']['rows']
    partial = manager_client.post('/manager/reports/monthly', json=dict(startDate='2026-06-15', endDate='2026-06-30'))
    assert partial.status_code == 201
    assert partial.json['report']['totals'] == dict(
        projectsCreated=9, shortlistSaves=24, topCategory='Bohemian Kitchen')
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'monthly'
        assert (saved.start_date, saved.end_date) == (date(2026, 6, 1), date(2026, 6, 30))
        assert saved.totals == report['totals']
        # The final instant of June in Singapore counts; 1 July in the fixture does not.
        for index in range(2):
            project = InteriorDesignProject()
            assert project.createNewProject(report_activity['designer'], f'June End Home {index + 1}',
                report_activity['transitional_id'], 'Apartment', 'Bedok', 80000, 'Created at the end of the month.')
            event = db.session.scalar(db.select(ActivityEvent).where(ActivityEvent.kind == 'project_new_created',
                ActivityEvent.target_id == str(project.project_id)))
            event.occurred_at = datetime(2026, 6, 30, 15, 59, 59, 999999, tzinfo=timezone.utc)
        db.session.commit()
    tied = manager_client.post('/manager/reports/monthly', json=dict(startDate='2026-06-01', endDate='2026-06-30'))
    assert tied.status_code == 201
    # Equal category counts use alphabetical order, making the top category stable.
    assert tied.json['report']['totals'] == dict(projectsCreated=12, shortlistSaves=32, topCategory='Bohemian Kitchen')
    assert tied.json['report']['rows'] == [dict(area='IDP categories', activity='Bohemian Kitchen', total=6),
                                         dict(area='IDP categories', activity='Transitional Kitchen', total=6)]
