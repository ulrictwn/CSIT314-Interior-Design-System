"""Sprint 2, user story 17: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story17]


def test_TC34_search_company_profile_returns_matching_details(designer_client, company_profile, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr('control.company.search_company_profile_controller.SearchCompanyProfileController.searchCompanyProfile',
                      lambda *args, **kwargs: pytest.fail('Malformed search input reached the controller.'))
        invalid = designer_client.get('/designer/company/search', query_string={'q': 'x' * 201})
        assert invalid.status_code == 400
        assert 'keyword' in invalid.json['errors']
    response = designer_client.get('/designer/company/search', query_string={'accountId': company_profile, 'q': 'Demo Studio'})
    assert response.status_code == 200
    assert response.json['results'] == ['Company name: Demo Studio']
