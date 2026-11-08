"""Sprint 3, user story 24: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story24]


def test_delete_new_project_removes_saved_project(app, designer_client, new_project, create_account, project_data):
    other_id = create_account('other_designer', 'Interior Designer')
    with app.app_context():
        other = InteriorDesignProject()
        assert other.createNewProject(other_id, **project_data)
        other_project_id = other.project_id
    base = f'/designer/projects/new/{other_project_id}'
    for suffix in ('', '/update', '/delete'):
        assert designer_client.get(base + suffix).status_code == 403
    for suffix in ('/update', '/delete'):
        assert designer_client.post(base + suffix, json=project_data).status_code == 403
    for suffix in ('views', 'shortlists'):
        assert designer_client.get(f'/designer/projects/{other_project_id}/{suffix}').status_code == 403
    with app.app_context():
        assert InteriorDesignProject.getNewProject(other_project_id).project_name == project_data['projectName']
    response = designer_client.post(f'/designer/projects/new/{new_project}/delete')
    assert response.status_code == 200
    with app.app_context():
        assert InteriorDesignProject.getNewProject(new_project) is None
