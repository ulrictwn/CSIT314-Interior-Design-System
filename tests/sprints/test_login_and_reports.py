from datetime import datetime, timezone
import csv,io
import pytest
from entity.accounts.user_account import UserAccount
from entity.reports.activity_event import ActivityEvent
from entity.reports.report import Report
from infrastructure.database import db

HTML={'Accept':'text/html'}
PASSWORD='Sprint-Demo-Password-123'


@pytest.mark.parametrize('role,username,password,target',[
    ('admin','admin','Review-Administrator-Password-123','/dashboard'),
    ('designer','designer1','Designer-Demo-Password-123','/designer'),
    ('manager','manager1',PASSWORD,'/manager')])
def test_staff_form_dispatches_to_role_and_dashboard(app,client,portal_accounts,admin_client,role,username,password,target):
    client.post('/logout')
    response=client.post('/staff/login',data=dict(staffRole=role,username=username,password=password),headers=HTML)
    assert response.status_code==302 and response.location==target
    assert client.get('/').location==target
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(ActivityEvent).where(ActivityEvent.kind=='login_success'))==2


def test_customer_wrong_role_failures_login_and_logout(client,portal_accounts):
    bad=client.post('/staff/login',json=dict(staffRole='manager',username='customer1',password=PASSWORD))
    assert bad.status_code==400 and 'Invalid login details' in bad.json['message']
    assert client.post('/customer/login',json=dict(username='manager1',password=PASSWORD)).status_code==400
    bad=client.post('/customer/login',data=dict(username='customer1',password='wrong'),headers=HTML)
    assert bad.status_code==400 and 'data-audience="customer"' in bad.text
    assert 'value="customer1"' in bad.text and 'value="wrong"' not in bad.text
    response=client.post('/customer/login',json=dict(username=' customer1 ',password=PASSWORD))
    assert response.status_code==302 and response.location=='/customer'
    assert client.get('/').location=='/customer' and client.get('/login').location=='/customer'
    with client.session_transaction() as session: assert session['account_id']==portal_accounts['customer1']
    response=client.post('/customer/logout',headers=HTML,follow_redirects=True)
    assert response.status_code==200 and 'signed out successfully' in response.text
    with client.session_transaction() as session: assert 'account_id' not in session


@pytest.mark.parametrize('role',['bad',None,True,[],{}])
def test_staff_role_selection_is_validated(client,role):
    response=client.post('/staff/login',json=dict(staffRole=role,username='any',password=PASSWORD))
    assert response.status_code==400 and 'staffRole' in response.json['errors']


@pytest.mark.parametrize('path',['/login','/staff/login','/designer/login','/manager/login','/customer/login'])
def test_login_pages_offer_staff_customer_and_all_staff_roles(client,path):
    page=client.get(path,headers=HTML)
    assert page.status_code==200 and 'data-login-audience="staff"' in page.text and 'data-login-audience="customer"' in page.text
    assert 'action="/staff/login"' in page.text and 'action="/customer/login"' in page.text
    assert all(role in page.text for role in ['Platform Manager','Interior Designer','User Admin'])


@pytest.mark.parametrize('path',['/manager/login','/customer/login'])
def test_role_login_input_validation(client,portal_accounts,path):
    for values in [dict(username='',password=PASSWORD),dict(username='x'*81,password=PASSWORD),dict(username='customer1',password='x'*129),dict(username=None,password=PASSWORD)]:
        response=client.post(path,json=values)
        assert response.status_code==400 and response.json['errors']


def test_report_singapore_day_boundaries_and_snapshot(app,client,portal_accounts):
    with app.app_context():
        for hour,day in [(15,4),(16,4),(15,5),(16,5)]:
            db.session.add(ActivityEvent(kind='login_success',occurred_at=datetime(2026,6,day,hour,0,tzinfo=timezone.utc)))
        db.session.add(ActivityEvent(kind='project_new_created',occurred_at=datetime(2026,6,5,1,tzinfo=timezone.utc)))
        db.session.add(ActivityEvent(kind='category_updated',occurred_at=datetime(2026,6,5,2,tzinfo=timezone.utc)))
        UserAccount.getUserAccount(portal_accounts['customer1']).created_at=datetime(2026,6,5,0,tzinfo=timezone.utc)
        db.session.commit()
    response=client.post('/manager/reports/daily',json=dict(startDate='2026-06-05',endDate='2026-06-05'))
    assert response.status_code==201
    report=response.json['report']; report_id=report['reportId']
    assert report['totals']==dict(successfulLogins=2,newRegistrations=1,projectsCreated=1)
    assert next(r['total'] for r in report['rows'] if r['activity']=='Categories updated')==1
    with app.app_context():
        db.session.add(ActivityEvent(kind='login_success',occurred_at=datetime(2026,6,5,3,tzinfo=timezone.utc)))
        db.session.commit()
        assert Report.getReport(report_id).totals['successfulLogins']==2
    download=client.get(f'/manager/reports/{report_id}/download')
    assert download.status_code==200 and download.mimetype=='text/csv'
    assert ['Successful logins','2'] in list(csv.reader(io.StringIO(download.text)))
    assert 'attachment;' in download.headers['Content-Disposition']
    refreshed=client.post('/manager/reports/daily',json=dict(startDate='2026-06-05',endDate='2026-06-05')).json['report']
    assert refreshed['reportId']!=report_id and refreshed['totals']['successfulLogins']==3
    assert client.get('/manager/reports/99999/download').status_code==404


@pytest.mark.parametrize('kind,start,end',[('daily','2026-06-05','2026-06-05'),('weekly','2026-06-01','2026-06-07'),('monthly','2026-06-01','2026-06-30')])
def test_report_html_generation_and_download(client,portal_accounts,kind,start,end):
    assert client.get('/manager/reports/'+kind,headers=HTML).status_code==200
    response=client.post('/manager/reports/'+kind,headers=HTML,data=dict(startDate=start,endDate=end,accountId=portal_accounts['manager1']))
    assert response.status_code==303
    page=client.get(response.location,headers=HTML)
    assert page.status_code==200 and 'Download CSV' in page.text and 'SGT' in page.text
    assert 'Past projects added' in page.text and 'Projects published' not in page.text
    assert client.get('/manager',headers=HTML).status_code==200


@pytest.mark.parametrize('kind,start,end',[
    ('daily','invalid','2026-01-01'),('daily','2026-01-01','2026-01-02'),
    ('weekly','2026-01-01','2026-01-01'),('weekly','2026-01-09','2026-01-01'),
    ('monthly','2026-02-01','2026-02-29'),('monthly','2026-02-02','2026-02-28'),
    ('daily','9999-12-31','9999-12-31'),('daily','0001-01-01','0001-01-01'),
    ('daily',None,'2026-01-01'),('daily',True,'2026-01-01')])
def test_invalid_report_dates_do_not_save(app,client,kind,start,end):
    response=client.post('/manager/reports/'+kind,json=dict(startDate=start,endDate=end))
    assert response.status_code==400 and response.json['errors']
    with app.app_context(): assert db.session.scalar(db.select(db.func.count()).select_from(Report))==0
