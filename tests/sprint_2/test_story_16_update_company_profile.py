"""Sprint 2, user story 16: one successful workflow through BCE."""
import pytest
from entity.company.company_profile import CompanyProfile

pytestmark = [pytest.mark.sprint2, pytest.mark.story16]


def test_update_company_profile_loads_and_saves_company_details(app, designer_client, company_profile, company_data, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr('control.company.update_company_profile_controller.UpdateCompanyProfileController.updateCompanyProfile',
                      lambda *args, **kwargs: pytest.fail('Malformed company input reached the controller.'))
        invalid = designer_client.post('/designer/company/update', json=dict(company_data,
            companyContact='letters', companyAddress=' '))
        assert invalid.status_code == 400
        assert {'companyContact', 'companyAddress'} <= invalid.json['errors'].keys()
    page = designer_client.get('/designer/company/update', query_string={'accountId': company_profile})
    assert page.status_code == 200
    assert page.json['values']['companyName'] == company_data['companyName']
    values = dict(company_data, companyName='Updated Studio', companyEmail='updated@example.com')
    response = designer_client.post('/designer/company/update', json=dict(accountId=company_profile, **values))
    assert response.status_code == 200
    with app.app_context():
        profile = CompanyProfile.getCompanyProfile(company_profile)
        assert (profile.company_name, profile.company_email) == ('Updated Studio', 'updated@example.com')
