"""Sprint 3, user story 28: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story28]


def test_TC45_search_past_projects_returns_matching_project(designer_client, past_project, designer_account):
    invalid = designer_client.post('/designer/projects/past/search', json={'projectName': []})
    assert invalid.status_code == 400
    assert 'projectName' in invalid.json['errors']
    response = designer_client.get('/designer/projects/past/search', query_string={'accountId': designer_account, 'q': 'Courtyard'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [past_project]
