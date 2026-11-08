"""Sprint 3, user story 20: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story20]


def test_create_new_project_saves_project_details(app, designer_client, designer_account, project_data):
    response = designer_client.post('/designer/projects/new/create', json=dict(accountId=designer_account, **project_data))
    assert response.status_code == 201
    project_id = response.json['project']['projectId']
    with app.app_context():
        project = InteriorDesignProject.getNewProject(project_id)
        assert (project.project_name, project.account_id, project.category_id) == (
            project_data['projectName'], designer_account, project_data['categoryId'])
        assert project.description == project_data['description']
