"""Sprint 4, user story 33: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story33]


def test_TC50_customer_searches_saved_projects(customer_client, customer_account, saved_project, past_project):
    # Invalid input passes through the controller and is rejected by the entity.
    invalid = customer_client.post('/customer/shortlist', json={'keyword': 'x' * 201})
    assert invalid.status_code == 400
    assert 'keyword' in invalid.json['errors']
    response = customer_client.get('/customer/shortlist', query_string={'accountId': customer_account, 'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [saved_project]
