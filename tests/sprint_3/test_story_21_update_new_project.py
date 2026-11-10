"""Sprint 3, user story 21: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story21]


def test_update_new_project_loads_and_saves_project_details(app, designer_client, new_project, project_data, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr('control.projects.update_new_project_controller.UpdateNewProjectController.updateNewProject',
                      lambda *args, **kwargs: pytest.fail('Malformed project input reached the controller.'))
        invalid = designer_client.post(f'/designer/projects/new/{new_project}/update',
            json=dict(project_data, renovationCost=-1, description=' '))
        assert invalid.status_code == 400
        assert {'renovationCost', 'description'} <= invalid.json['errors'].keys()
    page = designer_client.get(f'/designer/projects/new/{new_project}/update')
    assert page.status_code == 200
    assert page.json['values']['projectName'] == project_data['projectName']
    values = dict(project_data, projectName='Updated Seaside Home', renovationCost=90000)
    response = designer_client.post(f'/designer/projects/new/{new_project}/update', json=values)
    assert response.status_code == 200
    with app.app_context():
        project = InteriorDesignProject.getNewProject(new_project)
        assert (project.project_name, project.renovation_cost) == ('Updated Seaside Home', 90000)
