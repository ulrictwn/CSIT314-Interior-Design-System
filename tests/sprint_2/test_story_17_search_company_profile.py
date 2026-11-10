"""Sprint 2, user story 17: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story17]


def test_TC34_search_company_profile_returns_matching_details(designer_client, company_profile, company_data):
    updated = designer_client.post('/designer/company/update',
        json=dict(company_data, companyName='Updated Studio', companyEmail='updated@example.com'))
    assert updated.status_code == 200
    invalid = designer_client.get('/designer/company/search', query_string={'q': 'x' * 201})
    assert invalid.status_code == 400
    assert 'keyword' in invalid.json['errors']
    response = designer_client.get('/designer/company/search', query_string={'accountId': company_profile, 'q': 'Updated Studio'})
    assert response.status_code == 200
    assert response.json['results'] == ['Company name: Updated Studio']
