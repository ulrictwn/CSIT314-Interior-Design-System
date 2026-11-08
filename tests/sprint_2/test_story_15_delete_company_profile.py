"""Sprint 2, user story 15: one successful workflow through BCE."""
import pytest
from entity.company.company_profile import CompanyProfile

pytestmark = [pytest.mark.sprint2, pytest.mark.story15]


def test_delete_company_profile_removes_saved_profile(app, client, company_profile):
    confirmation = client.get('/designer/company/delete', query_string={'accountId': company_profile})
    assert confirmation.status_code == 200
    assert confirmation.json['confirmationRequired'] is True
    response = client.post('/designer/company/delete', json={'accountId': company_profile})
    assert response.status_code == 200
    with app.app_context():
        assert CompanyProfile.getCompanyProfile(company_profile) is None
