"""Sprint 3, user story 28: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story28]


def test_search_past_projects_returns_matching_project(client, past_project, designer_account):
    response = client.get('/designer/projects/past/search', query_string={'accountId': designer_account, 'q': 'Courtyard'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [past_project]
