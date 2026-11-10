"""Sprint 3, user story 25: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story25]


def test_create_past_project_saves_project_details(app, designer_client, designer_account, project_data, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr('control.projects.create_past_project_controller.CreatePastProjectController.createPastProject',
                      lambda *args, **kwargs: pytest.fail('Malformed project input reached the controller.'))
        invalid = designer_client.post('/designer/projects/past/create', json=dict(project_data,
            projectName=' ', categoryId='invalid-id', renovationCost='nan'))
        assert invalid.status_code == 400
        assert {'projectName', 'categoryId', 'renovationCost'} <= invalid.json['errors'].keys()
    response = designer_client.post('/designer/projects/past/create', json=dict(accountId=designer_account, **project_data))
    assert response.status_code == 201
    project_id = response.json['project']['projectId']
    with app.app_context():
        project = InteriorDesignProject.getPastProject(project_id)
        assert (project.project_name, project.account_id, project.category_id) == (
            project_data['projectName'], designer_account, project_data['categoryId'])
        assert project.description == project_data['description']
    duplicate = designer_client.post('/designer/projects/past/create', json=dict(
        accountId=designer_account, **dict(project_data, projectName=project_data['projectName'].upper())))
    assert duplicate.status_code == 400
    assert 'projectName' in duplicate.json['errors']
