"""Sprint 2, user story 15: one successful workflow through BCE."""
import pytest
from entity.company.company_profile import CompanyProfile

pytestmark = [pytest.mark.sprint2, pytest.mark.story15]


def test_TC32_delete_company_profile_removes_saved_profile(app, designer_client, company_profile, create_account, company_data):
    other_id = create_account('other_designer', 'Interior Designer')
    with app.app_context():
        assert CompanyProfile().createCompanyProfile(other_id, **dict(company_data, companyRegistrationNumber='OTHER-123'))
    for response in (
        designer_client.get('/designer/company/delete', query_string={'accountId': other_id}),
        designer_client.post('/designer/company/delete', json={'accountId': other_id}),
        designer_client.post('/designer/company/delete', data={'accountId': other_id}),
    ):
        assert response.status_code == 403
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(other_id) is not None
        assert CompanyProfile.getCompanyProfile(company_profile) is not None
    confirmation = designer_client.get('/designer/company/delete', query_string={'accountId': company_profile})
    assert confirmation.status_code == 200
    assert confirmation.json['confirmationRequired'] is True
    response = designer_client.post('/designer/company/delete', json={'accountId': company_profile})
    assert response.status_code == 200
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(company_profile) is None
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(other_id) is not None
