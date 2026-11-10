"""Sprint 5, user story 46: display and save the required daily IDP statistics."""
import csv
from datetime import date
import io

import pytest
from entity.reports.report import Report

pytestmark = [pytest.mark.sprint5, pytest.mark.story46]


def test_TC63_generate_daily_report_displays_and_saves_period_totals(app, manager_client, report_activity):
    # Invalid input passes through the controller and is rejected by the entity.
    invalid = manager_client.post('/manager/reports/daily', json={'startDate': 'not-a-date'})
    assert invalid.status_code == 400
    assert 'startDate' in invalid.json['errors']
    with app.app_context():
        assert Report.query.count() == 0
    response = manager_client.post('/manager/reports/daily', json=dict(startDate=' 2026-11-04 '))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'daily', '2026-11-04', '2026-11-04')
    assert report['totals'] == report_activity['daily']['totals']
    assert report['rows'] == report_activity['daily']['rows']
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'daily'
        assert (saved.start_date, saved.end_date) == (date(2026, 11, 4), date(2026, 11, 4))
        assert saved.totals == report['totals']
        assert saved.rows == report['rows']

    page = manager_client.get('/manager/reports/' + str(report['reportId']), headers={'Accept': 'text/html'})
    assert page.status_code == 200
    for label in (b'New IDPs created', b'Customer shortlists', b'Top IDP category', b'Bohemian Living room'):
        assert label in page.data
    assert b'Successful logins' not in page.data and b'New registrations' not in page.data
    download = manager_client.get('/manager/reports/' + str(report['reportId']) + '/download')
    assert download.status_code == 200
    rows = list(csv.reader(io.StringIO(download.get_data(as_text=True))))
    assert ['New IDPs created', '2'] in rows
    assert ['Customer shortlists', '2'] in rows
    assert ['Top IDP category', 'Bohemian Living room'] in rows
    assert ['Bohemian Living room', '2'] in rows

    empty = manager_client.post('/manager/reports/daily', json=dict(startDate='2026-08-01'))
    assert empty.status_code == 201
    assert empty.json['report']['totals'] == dict(projectsCreated=0, shortlistSaves=0, topCategory=None)
    assert empty.json['report']['rows'] == []
    empty_page = manager_client.get('/manager/reports/' + str(empty.json['report']['reportId']),
                                   headers={'Accept': 'text/html'})
    assert empty_page.status_code == 200
    assert b'No new IDPs' in empty_page.data
