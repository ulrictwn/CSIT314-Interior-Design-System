"""Sprint 2, user story 14: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story14]


def test_view_company_profile_displays_saved_details(client, company_profile, company_data):
    response = client.get('/designer/company', query_string={'accountId': company_profile})
    assert response.status_code == 200
    assert response.json['profile'] == dict(accountId=company_profile, **company_data)
