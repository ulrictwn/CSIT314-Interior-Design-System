from datetime import date
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from boundary.reports.daily_report_page import DailyReportPage
from boundary.reports.weekly_report_page import WeeklyReportPage
from boundary.reports.monthly_report_page import MonthlyReportPage
from control.reports.daily_report_controller import DailyReportController
from control.reports.weekly_report_controller import WeeklyReportController
from control.reports.monthly_report_controller import MonthlyReportController
from entity.reports.report import Report
from infrastructure.database import db


@pytest.mark.parametrize('controller,operation,arguments,kind,expected_end',[
    (DailyReportController,'generateDailyReport',[date(2026,6,1)],'daily',date(2026,6,1)),
    (WeeklyReportController,'generateWeeklyReport',[date(2026,6,1)],'weekly',date(2026,6,7)),
    (MonthlyReportController,'generateMonthlyReport',[date(2026,6,1),date(2026,6,30)],'monthly',date(2026,6,30)),
])
def test_each_report_controller_relays_to_the_shared_entity_method(monkeypatch,controller,operation,arguments,kind,expected_end):
    calls=[]; result=object()
    def generate(entity,reportType,startDate,endDate):
        calls.append((entity.account_id,reportType,startDate,endDate))
        return result
    monkeypatch.setattr(Report,'generateReport',generate)
    assert getattr(controller(accountId='101'),operation)(*arguments) is result
    assert calls==[('101',kind,date(2026,6,1),expected_end)]


@pytest.mark.parametrize('page,controller,event,operation,arguments',[
    (DailyReportPage,DailyReportController,'onGenerateDailyReport','generateDailyReport',[date(2026,6,1)]),
    (WeeklyReportPage,WeeklyReportController,'onGenerateWeeklyReport','generateWeeklyReport',[date(2026,6,1)]),
    (MonthlyReportPage,MonthlyReportController,'onGenerateMonthlyReport','generateMonthlyReport',[date(2026,6,1),date(2026,6,30)]),
])
def test_report_boundary_event_receives_dates_and_displays_the_returned_report(app,monkeypatch,page,controller,event,operation,arguments):
    report=object(); call=Mock(return_value=report)
    monkeypatch.setattr(controller,operation,call)
    with app.test_request_context('/manager/reports/daily',method='POST'):
        boundary=page(); boundary.displayReport=Mock()
        assert getattr(boundary,event)(*arguments) is None
        call.assert_called_once_with(*arguments)
        boundary.displayReport.assert_called_once_with(report)


@pytest.mark.parametrize('kind,end',[('daily','2026-06-01'),('weekly','2026-06-07')])
def test_daily_weekly_http_inputs_need_only_the_diagram_start_date(client,kind,end):
    response=client.post('/manager/reports/'+kind,json={'startDate':'2026-06-01'})
    assert response.status_code==201 and response.json['report']['endDate']==end
    html=client.get('/manager/reports/'+kind,headers={'Accept':'text/html'}).text
    assert 'name="endDate"' not in html
    assert 'readonly' in html


def test_monthly_http_input_keeps_both_diagram_dates(client):
    assert client.post('/manager/reports/monthly',json={'startDate':'2026-06-01'}).status_code==400
    response=client.post('/manager/reports/monthly',json={'startDate':'2026-06-01','endDate':'2026-06-30'})
    assert response.status_code==201 and response.json['report']['endDate']=='2026-06-30'
    assert 'name="endDate"' in client.get('/manager/reports/monthly',headers={'Accept':'text/html'}).text


@pytest.mark.parametrize('kind,start,end',[('invalid',date(2026,6,1),date(2026,6,1)),
                                           ('daily',date(2026,6,2),date(2026,6,1))])
def test_database_rejects_report_types_and_reversed_ranges(app,kind,start,end):
    with app.app_context():
        db.session.add(Report(report_type=kind,start_date=start,end_date=end,totals={},rows=[]))
        with pytest.raises(IntegrityError):db.session.commit()
        db.session.rollback()
