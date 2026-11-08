"""Sprint 3, user story 23: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story23]


def test_search_new_projects_returns_matching_project(client, new_project, designer_account):
    response = client.get('/designer/projects/new/search', query_string={'accountId': designer_account, 'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [new_project]
