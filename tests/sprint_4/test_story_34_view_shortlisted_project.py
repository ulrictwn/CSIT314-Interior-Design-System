"""Sprint 4, user story 34: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story34]


def test_customer_views_saved_project_details(customer_client, customer_account, saved_project, project_data):
    response = customer_client.get(f'/customer/shortlist/{saved_project}', query_string={'accountId': customer_account})
    assert response.status_code == 200
    project = response.json['project']
    assert project['projectId'] == saved_project
    for field, value in project_data.items():
        assert project[field] == value
