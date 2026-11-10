"""Sprint 2, user story 13: one successful workflow through BCE."""
import pytest
from entity.company.company_profile import CompanyProfile

pytestmark = [pytest.mark.sprint2, pytest.mark.story13]


def test_TC30_create_company_profile_saves_company_details(app, designer_client, designer_account, company_data):
    invalid = designer_client.post('/designer/company/create', json=dict(company_data,
        companyName=' ', companyEmail='invalid-email'))
    assert invalid.status_code == 400
    assert {'companyName', 'companyEmail'} <= invalid.json['errors'].keys()
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(designer_account) is None
    response = designer_client.post('/designer/company/create', json=dict(accountId=designer_account, **company_data))
    assert response.status_code == 201
    assert response.json['profile'] == dict(accountId=designer_account, **company_data)
    with app.app_context():
        profile = CompanyProfile.getCompanyProfile(designer_account)
        assert profile.company_name == company_data['companyName']
        assert profile.company_registration_number == company_data['companyRegistrationNumber']
    duplicate = designer_client.post('/designer/company/create', json=dict(accountId=designer_account, **company_data))
    assert duplicate.status_code == 400
