"""Sprint 3, user story 29: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story29]


def test_delete_past_project_removes_saved_project(app, client, past_project):
    response = client.post(f'/designer/projects/past/{past_project}/delete')
    assert response.status_code == 200
    with app.app_context():
        assert InteriorDesignProject.getPastProject(past_project) is None
