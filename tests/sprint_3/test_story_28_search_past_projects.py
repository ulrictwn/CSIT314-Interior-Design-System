"""Sprint 3, user story 28: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story28]


def test_search_past_projects_returns_matching_project(designer_client, past_project, designer_account, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr('control.projects.search_past_project_controller.SearchPastProjectController.searchPastProjects',
                      lambda *args, **kwargs: pytest.fail('Malformed search input reached the controller.'))
        invalid = designer_client.post('/designer/projects/past/search', json={'projectName': []})
        assert invalid.status_code == 400
        assert 'projectName' in invalid.json['errors']
    response = designer_client.get('/designer/projects/past/search', query_string={'accountId': designer_account, 'q': 'Courtyard'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [past_project]
