"""Sprint 2, user story 10: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story10]


def test_search_user_account_returns_matching_account(client, customer_account):
    response = client.get('/accounts/search', query_string={'q': 'customer1'})
    assert response.status_code == 200
    assert 'customer1@example.com' in response.text
    assert f'href="/accounts/{customer_account}"' in response.text
