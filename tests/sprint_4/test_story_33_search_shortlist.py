"""Sprint 4, user story 33: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story33]


def test_customer_searches_saved_projects(client, customer_account, saved_project, past_project):
    response = client.get('/customer/shortlist', query_string={'accountId': customer_account, 'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [saved_project]
