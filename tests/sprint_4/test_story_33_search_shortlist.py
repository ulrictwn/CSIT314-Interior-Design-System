"""Sprint 4, user story 33: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock

pytestmark = [pytest.mark.sprint4, pytest.mark.story33]


def test_TC50_customer_searches_saved_projects(customer_client, customer_account, saved_project, past_project, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.customer.search_shortlist_idp_page.SearchShortlistIDPController.search_shortlist_IDP', blocked)
        invalid = customer_client.post('/customer/shortlist', json={'keyword': 'x' * 201})
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = customer_client.get('/customer/shortlist', query_string={'accountId': customer_account, 'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [saved_project]
