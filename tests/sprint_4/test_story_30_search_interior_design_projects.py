"""Sprint 4, user story 30: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock

pytestmark = [pytest.mark.sprint4, pytest.mark.story30]


def test_TC47_customer_search_returns_matching_project(customer_client, new_project, past_project, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.customer.search_idp_page.SearchIDPController.search_all_IDPs', blocked)
        invalid = customer_client.post('/customer/projects', json={'keyword': ['invalid']})
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = customer_client.get('/customer/projects', query_string={'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [new_project]
