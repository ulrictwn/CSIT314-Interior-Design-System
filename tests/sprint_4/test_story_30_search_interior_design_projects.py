"""Sprint 4, user story 30: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story30]


def test_customer_search_returns_matching_project(customer_client, new_project, past_project):
    response = customer_client.get('/customer/projects', query_string={'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [new_project]
