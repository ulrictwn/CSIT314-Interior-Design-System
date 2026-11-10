"""Sprint 2, user story 10: one successful workflow through BCE."""
import pytest
from unittest.mock import patch

pytestmark = [pytest.mark.sprint2, pytest.mark.story10]


def test_search_user_account_returns_matching_account(admin_client, customer_account):
    response = admin_client.get('/accounts/search', query_string={'q': 'customer1'})
    assert response.status_code == 200
    assert 'customer1@example.com' in response.text
    assert f'href="/accounts/{customer_account}"' in response.text

    with patch('boundary.accounts.search_user_account_page.SearchUserAccountController.searchUserAccounts') as search:
        invalid = admin_client.get('/accounts/search', query_string={'q': 'x' * 201})
        assert invalid.status_code == 200
        assert 'Search text must be at most 200 characters.' in invalid.text
        search.assert_not_called()
