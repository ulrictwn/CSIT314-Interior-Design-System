"""Browser representations exercise the same BCE events as the JSON adapters."""
from urllib.parse import parse_qs, urlsplit

import pytest

from entity.company.company_profile import CompanyProfile
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.database import db


HTML = {'Accept': 'text/html'}
PASSWORD = 'Designer-Demo-Password-123'


@pytest.fixture
def workspace(client, designer_accounts, company_data, project_data):
    owner, _ = designer_accounts
    assert client.post('/designer/company/create', json=dict(company_data, accountId=owner)).status_code == 201
    projects = {}
    for phase in ('new', 'past'):
        response = client.post(f'/designer/projects/{phase}/create', json=dict(project_data, accountId=owner))
        assert response.status_code == 201
        projects[phase] = response.json['project']['projectId']
    return owner, projects


@pytest.mark.parametrize('path,role', [('/login', 'admin'), ('/designer/login', 'designer')])
def test_login_html_has_separate_submission_handlers(client, path, role):
    response = client.get(path, headers=HTML)
    text = response.get_data(as_text=True)
    assert response.status_code == 200 and response.mimetype == 'text/html'
    assert f'data-role="{role}"' in text
    assert 'action="/staff/login"' in text and 'action="/customer/login"' in text
    assert 'data-login-audience="staff"' in text and 'data-login-audience="customer"' in text
    assert 'login.js' in text


def test_designer_login_errors_and_logout_render_in_the_selected_panel(client, designer_accounts):
    response = client.post('/designer/login', data=dict(username='designer1', password='incorrect'), headers=HTML)
    text = response.get_data(as_text=True)
    assert response.status_code == 400 and 'data-role="designer"' in text
    assert 'Invalid login details' in text and 'value="designer1"' in text
    assert 'incorrect' not in text
    response = client.post('/designer/login', data=dict(username='designer1', password=PASSWORD), headers=HTML)
    assert response.status_code == 302 and response.location == '/designer'
    response = client.get('/designer', headers=HTML)
    assert response.status_code == 200 and 'Company profile' in response.get_data(as_text=True)
    assert client.get('/').location == '/designer'
    response = client.post('/designer/logout', headers=HTML, follow_redirects=True)
    assert response.status_code == 200 and 'signed out successfully' in response.get_data(as_text=True)


def test_designer_html_is_available_without_login_and_preserves_explicit_owner(client, designer_accounts):
    owner, _ = designer_accounts
    response = client.get('/designer', headers=HTML, query_string={'accountId': owner})
    text = response.get_data(as_text=True)
    assert response.status_code == 200 and f'/designer/company/create?accountId={owner}' in text
    response = client.get('/designer/company', headers=HTML)
    assert response.status_code == 400 and 'name="accountId"' in response.get_data(as_text=True)
    # Direct API clients keep their existing JSON response, even on browser-capable routes.
    assert client.get('/designer').is_json
    assert client.get('/designer', headers=HTML, query_string={'format':'json'}).is_json


@pytest.mark.parametrize('operation', ['', '/create', '/update', '/delete', '/search'])
def test_company_pages_display_saved_values_or_inputs(client, workspace, operation):
    owner, _ = workspace
    response = client.get('/designer/company'+operation, headers=HTML, query_string={'accountId':owner})
    text = response.get_data(as_text=True)
    assert response.status_code == 200 and response.mimetype == 'text/html'
    assert str(owner) in text
    if operation != '/create':
        assert 'Demo Studio' in text
    if operation in ('/create', '/update'):
        assert 'name="companyRegistrationNumber"' in text
    if operation == '/delete':
        assert 'Are you sure' in text and 'method="post"' in text


def test_company_validation_preserves_input_and_success_redirects_to_saved_record(app, client, designer_accounts, company_data):
    owner, _ = designer_accounts
    invalid = dict(company_data, accountId=owner, companyName='   ', companyEmail='bad-email')
    response = client.post('/designer/company/create', data=invalid, headers=HTML)
    text = response.get_data(as_text=True)
    assert response.status_code == 400 and 'role="alert"' in text
    assert 'value="bad-email"' in text and 'value="DEMO-123"' in text
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(owner) is None
    response = client.post('/designer/company/create', data=dict(company_data, accountId=owner), headers=HTML)
    assert response.status_code == 303 and urlsplit(response.location).path == '/designer/company'
    assert parse_qs(urlsplit(response.location).query)['accountId'] == [owner]
    detail = client.get(response.location, headers=HTML).get_data(as_text=True)
    assert 'created successfully' in detail and 'Demo Studio' in detail
    response = client.post('/designer/company/create', data=dict(company_data, accountId=owner), headers=HTML)
    assert response.status_code == 400 and 'already has a company profile' in response.get_data(as_text=True)


def test_company_search_and_delete_confirmation_do_not_modify_data(app, client, workspace):
    owner, _ = workspace
    response = client.get('/designer/company/search', headers=HTML, query_string={'accountId':owner, 'q':'Demo Road'})
    text = response.get_data(as_text=True)
    assert text.count('class="company-result"') == 1 and '10 Demo Road' in text
    assert client.get('/designer/company/delete', headers=HTML, query_string={'accountId':owner}).status_code == 200
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(owner) is not None
    response = client.post('/designer/company/delete', data={'accountId':owner}, headers=HTML)
    assert response.status_code == 303 and urlsplit(response.location).path == '/designer/company/search'
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(owner) is None


@pytest.mark.parametrize('phase', ['new', 'past'])
def test_project_forms_detail_and_delete_pages_render_the_record(app, client, workspace, phase):
    owner, projects = workspace
    project_id = projects[phase]
    for suffix in ('', '/update', '/delete'):
        response = client.get(f'/designer/projects/{phase}/{project_id}'+suffix, headers=HTML)
        text = response.get_data(as_text=True)
        assert response.status_code == 200 and 'Seaside Home' in text
        assert str(owner) in text
        if suffix == '/update':
            assert 'name="categoryId"' in text and 'value="1"' in text
            assert 'name="description"' in text and 'A bright renovation project.' in text
    # A confirmation GET has no delete side effect.
    with app.app_context():
        assert db.session.get(InteriorDesignProject, project_id) is not None


@pytest.mark.parametrize('phase', ['new', 'past'])
@pytest.mark.parametrize('mode,label', [('view','View'), ('search','View'), ('update','Update'), ('delete','Delete')])
def test_project_collection_offers_the_selected_operation(client, workspace, phase, mode, label):
    owner, projects = workspace
    response = client.get(f'/designer/projects/{phase}', headers=HTML,
        query_string={'accountId':owner, 'q':'seaside', 'mode':mode})
    text = response.get_data(as_text=True)
    assert response.status_code == 200 and 'Seaside Home' in text
    suffix = '/'+mode if mode in ('update', 'delete') else ''
    assert f'/designer/projects/{phase}/{projects[phase]}{suffix}?accountId={owner}' in text
    assert f'>{label}</a>' in text
    assert f'name="mode" value="{mode}"' in text


@pytest.mark.parametrize('phase', ['new', 'past'])
def test_project_create_update_validation_and_delete_html(app, client, designer_accounts, project_data, phase):
    owner, _ = designer_accounts
    root = f'/designer/projects/{phase}'
    response = client.post(root+'/create', headers=HTML, data=dict(project_data, accountId=owner))
    assert response.status_code == 303
    detail_url = response.location
    project_id = int(urlsplit(detail_url).path.rsplit('/',1)[1])
    invalid = dict(project_data, accountId=owner, renovationCost='-1', description='Keep this submitted description')
    response = client.post(f'{root}/{project_id}/update', headers=HTML, data=invalid)
    text = response.get_data(as_text=True)
    assert response.status_code == 400 and 'Keep this submitted description' in text
    assert 'value="-1"' in text and 'role="alert"' in text
    with app.app_context():
        assert db.session.get(InteriorDesignProject, project_id).renovation_cost == project_data['renovationCost']
    response = client.post(f'{root}/{project_id}/update', headers=HTML,
        data=dict(project_data, accountId=owner, projectName='Updated Home'))
    assert response.status_code == 303
    text = client.get(response.location, headers=HTML).get_data(as_text=True)
    assert 'Updated Home' in text and 'updated successfully' in text
    response = client.post(f'{root}/{project_id}/delete', headers=HTML, data={'accountId':owner})
    assert response.status_code == 303
    text = client.get(response.location, headers=HTML).get_data(as_text=True)
    assert 'deleted successfully' in text and 'No projects found' in text
    assert client.get(detail_url, headers=HTML).status_code == 404
