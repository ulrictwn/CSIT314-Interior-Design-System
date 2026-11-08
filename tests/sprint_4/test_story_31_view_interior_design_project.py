"""Sprint 4, user story 31: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story31]


def test_customer_view_displays_project_details(client, new_project, project_data):
    response = client.get(f'/customer/projects/{new_project}')
    assert response.status_code == 200
    project = response.json['project']
    assert project['projectId'] == new_project
    for field, value in project_data.items():
        assert project[field] == value
