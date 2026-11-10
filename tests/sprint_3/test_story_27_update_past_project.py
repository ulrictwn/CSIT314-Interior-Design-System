"""Sprint 3, user story 27: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story27]


def test_update_past_project_loads_and_saves_project_details(app, designer_client, past_project, project_data, monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr('control.projects.update_past_project_controller.UpdatePastProjectController.updatePastProject',
                      lambda *args, **kwargs: pytest.fail('Malformed project input reached the controller.'))
        invalid = designer_client.post(f'/designer/projects/past/{past_project}/update',
            json=dict(project_data, renovationCost=-1, description=' '))
        assert invalid.status_code == 400
        assert {'renovationCost', 'description'} <= invalid.json['errors'].keys()
    page = designer_client.get(f'/designer/projects/past/{past_project}/update')
    assert page.status_code == 200
    assert page.json['values']['projectName'] == 'Courtyard Retreat'
    values = dict(project_data, projectName='Updated Courtyard', description='Updated past project')
    response = designer_client.post(f'/designer/projects/past/{past_project}/update', json=values)
    assert response.status_code == 200
    with app.app_context():
        project = InteriorDesignProject.getPastProject(past_project)
        assert (project.project_name, project.description) == ('Updated Courtyard', 'Updated past project')
