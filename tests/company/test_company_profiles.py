from unittest.mock import Mock
import pytest

from boundary.company.create_company_profile_page import CreateCompanyProfilePage
from boundary.company.update_company_profile_page import UpdateCompanyProfilePage
from control.company.create_company_profile_controller import CreateCompanyProfileController
from control.company.update_company_profile_controller import UpdateCompanyProfileController
from entity.accounts.user_account import UserAccount
from entity.company.company_profile import CompanyProfile
from infrastructure.database import db


@pytest.mark.story13
@pytest.mark.story14
@pytest.mark.story15
@pytest.mark.story16
@pytest.mark.story17
def test_company_lifecycle_json_and_form_input(app, client, designer_accounts, company_data):
    owner, other = designer_accounts
    raw = {key: '  '+value+'  ' for key, value in company_data.items()}
    response = client.post('/designer/company/create', json=dict(accountId=owner, **raw))
    assert response.status_code == 201
    assert response.json['profile'] == dict(accountId=owner, **company_data)
    response = client.get('/designer/company', query_string={'accountId': owner})
    assert response.status_code == 200 and response.json['profile']['companyName'] == company_data['companyName']
    assert client.get('/designer/company', query_string={'accountId': other}).status_code == 404
    prefill = client.get('/designer/company/update', query_string={'accountId': owner})
    assert prefill.json['values']['companyRegistrationNumber'] == company_data['companyRegistrationNumber']
    changed = dict(company_data, companyName='Updated Studio', companyEmail='new@example.com')
    assert client.post('/designer/company/update', data=dict(accountId=owner, **changed)).status_code == 200
    response = client.get('/designer/company/search', query_string={'accountId': owner, 'q': ' updated '})
    assert response.json['results'] == ['Company name: Updated Studio']
    response = client.get('/designer/company/search', query_string={'accountId': owner, 'q': ''})
    assert len(response.json['results']) == 5 and all(isinstance(v, str) for v in response.json['results'])
    confirmation = client.get('/designer/company/delete', query_string={'accountId': owner})
    assert confirmation.json['confirmationRequired'] is True
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(owner) is not None
    assert client.post('/designer/company/delete', json={'accountId': owner}).status_code == 200
    assert client.post('/designer/company/delete', json={'accountId': owner}).status_code == 404
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(owner) is None
        assert UserAccount.getUserAccount(owner) is not None


@pytest.mark.parametrize('patch,field', [
    ({'companyName': ''}, 'companyName'), ({'companyName': None}, 'companyName'),
    ({'companyName': 'x'*151}, 'companyName'),
    ({'companyContact': 'letters'}, 'companyContact'), ({'companyContact': ''}, 'companyContact'),
    ({'companyAddress': '   '}, 'companyAddress'), ({'companyAddress': 'x'*1001}, 'companyAddress'),
    ({'companyEmail': 'not-email'}, 'companyEmail'), ({'companyEmail': None}, 'companyEmail'),
    ({'companyRegistrationNumber': ''}, 'companyRegistrationNumber'),
    ({'companyRegistrationNumber': 'x'*101}, 'companyRegistrationNumber'),
])
@pytest.mark.parametrize('action', ['Create', 'Update'])
def test_company_boundary_rejects_fields_before_controller(company_data, monkeypatch, patch, field, action):
    page_type = CreateCompanyProfilePage if action == 'Create' else UpdateCompanyProfilePage
    controller = CreateCompanyProfileController if action == 'Create' else UpdateCompanyProfileController
    method = action.lower()+'CompanyProfile'
    operation = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    monkeypatch.setattr(controller, method, operation)
    page = page_type(accountId='101')
    assert getattr(page, 'on'+action)(**{**company_data, **patch}) is None
    assert page.rendered_page[1] == 400 and field in page.field_errors
    operation.assert_not_called()


@pytest.mark.story13
@pytest.mark.story16
def test_company_entity_duplicates_and_rollback(app, designer_accounts, company_data, monkeypatch):
    owner, other = designer_accounts
    with app.app_context():
        assert CompanyProfile().createCompanyProfile(owner, **company_data) is True
        operation = CompanyProfile()
        assert operation.createCompanyProfile(owner, **dict(company_data, companyRegistrationNumber='OTHER')) is False
        assert 'already' in operation.error_message
        operation = CompanyProfile()
        assert operation.createCompanyProfile(other, **dict(company_data, companyRegistrationNumber='demo-123')) is False
        assert operation.field_errors['companyRegistrationNumber']
        # The database uniqueness constraint must also handle a competing insert.
        monkeypatch.setattr(CompanyProfile, '_registration_exists', lambda *args: False)
        assert CompanyProfile().createCompanyProfile(other, **company_data) is False
        second = dict(company_data, companyName='Other Studio', companyRegistrationNumber='OTHER')
        assert CompanyProfile().createCompanyProfile(other, **second) is True
        monkeypatch.undo()
        assert CompanyProfile().updateCompanyProfile(owner, **dict(company_data, companyRegistrationNumber='other')) is False
        assert CompanyProfile.getCompanyProfile(owner).company_registration_number == 'DEMO-123'
        assert CompanyProfile().updateCompanyProfile(owner, **company_data) is True
        assert len(db.session.scalars(db.select(CompanyProfile)).all()) == 2


@pytest.mark.parametrize('path', ['/designer/company', '/designer/company/update', '/designer/company/delete'])
def test_company_missing_context_is_input_error(client, path):
    response = client.get(path)
    assert response.status_code == 400 and response.is_json


def test_company_missing_account_or_profile_is_data_error(app, designer_accounts, company_data):
    owner, _ = designer_accounts
    with app.app_context():
        operation = CompanyProfile()
        assert operation.createCompanyProfile('missing-account', **company_data) is False
        assert operation.error_reason == 'not_found'
        assert CompanyProfile().updateCompanyProfile(owner, **company_data) is False
        assert CompanyProfile().deleteCompanyProfile(owner) is False
        assert CompanyProfile.searchCompanyProfile(owner, '') == []


def test_invalid_company_edit_keeps_saved_values(app, client, designer_accounts, company_data):
    owner, _ = designer_accounts
    assert client.post('/designer/company/create', json=dict(accountId=owner, **company_data)).status_code == 201
    response = client.post('/designer/company/update', json=dict(accountId=owner, **{
        **company_data, 'companyEmail': 'invalid', 'companyName': 'Unsaved edit'}))
    assert response.status_code == 400
    assert response.json['values']['companyName'] == 'Unsaved edit'
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(owner).company_name == company_data['companyName']


def test_company_search_is_scoped_to_account(app, designer_accounts, company_data):
    owner, other = designer_accounts
    with app.app_context():
        assert CompanyProfile().createCompanyProfile(owner, **company_data)
        assert CompanyProfile().createCompanyProfile(other, **dict(company_data,
            companyName='Private Other Studio', companyRegistrationNumber='OTHER'))
        assert CompanyProfile.searchCompanyProfile(owner, 'Private Other') == []
        assert CompanyProfile.searchCompanyProfile(other, 'private other') == ['Company name: Private Other Studio']
