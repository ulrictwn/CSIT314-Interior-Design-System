"""Sprint 5, user story 46: display and save the required daily IDP statistics."""
import csv
from datetime import date
import io

import pytest
from entity.reports.report import Report

pytestmark = [pytest.mark.sprint5, pytest.mark.story46]


def test_generate_daily_report_displays_and_saves_period_totals(app, manager_client, report_activity):
    response = manager_client.post('/manager/reports/daily', json=dict(startDate=' 2026-06-05 '))
    assert response.status_code == 201
    report = response.json['report']
    assert (report['type'], report['startDate'], report['endDate']) == (
        'daily', '2026-06-05', '2026-06-05')
    assert report['totals'] == report_activity['totals']
    assert report['rows'] == report_activity['rows']
    with app.app_context():
        saved = Report.getReport(report['reportId'])
        assert saved.report_type == 'daily'
        assert (saved.start_date, saved.end_date) == (date(2026, 6, 5), date(2026, 6, 5))
        assert saved.totals == report['totals']
        assert saved.rows == report['rows']

    page = manager_client.get('/manager/reports/' + str(report['reportId']), headers={'Accept': 'text/html'})
    assert page.status_code == 200
    for label in (b'New IDPs created', b'Customer shortlists', b'Top IDP category', b'Scandinavian'):
        assert label in page.data
    assert b'Successful logins' not in page.data and b'New registrations' not in page.data
    download = manager_client.get('/manager/reports/' + str(report['reportId']) + '/download')
    assert download.status_code == 200
    rows = list(csv.reader(io.StringIO(download.get_data(as_text=True))))
    assert ['New IDPs created', '3'] in rows
    assert ['Customer shortlists', '3'] in rows
    assert ['Top IDP category', 'Scandinavian'] in rows
    assert ['Scandinavian', '2'] in rows

    empty = manager_client.post('/manager/reports/daily', json=dict(startDate='2026-08-01'))
    assert empty.status_code == 201
    assert empty.json['report']['totals'] == dict(projectsCreated=0, shortlistSaves=0, topCategory=None)
    assert empty.json['report']['rows'] == []
    empty_page = manager_client.get('/manager/reports/' + str(empty.json['report']['reportId']),
                                   headers={'Accept': 'text/html'})
    assert empty_page.status_code == 200
    assert b'No new IDPs' in empty_page.data
