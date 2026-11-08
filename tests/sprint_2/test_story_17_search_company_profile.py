"""Sprint 2, user story 17: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story17]


def test_search_company_profile_returns_matching_details(client, company_profile):
    response = client.get('/designer/company/search', query_string={'accountId': company_profile, 'q': 'Demo Studio'})
    assert response.status_code == 200
    assert response.json['results'] == ['Company name: Demo Studio']
