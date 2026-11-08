"""Sprint 4, user story 38: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story38]


def test_designer_views_project_shortlist_count(client, saved_project):
    response = client.get(f'/designer/projects/{saved_project}/shortlists')
    assert response.status_code == 200
    assert response.json['project']['projectId'] == saved_project
    assert response.json['count'] == 1
