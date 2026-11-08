"""Sprint 3, user story 24: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story24]


def test_delete_new_project_removes_saved_project(app, client, new_project):
    response = client.post(f'/designer/projects/new/{new_project}/delete')
    assert response.status_code == 200
    with app.app_context():
        assert InteriorDesignProject.getNewProject(new_project) is None
