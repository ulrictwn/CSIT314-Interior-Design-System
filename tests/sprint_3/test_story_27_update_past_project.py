"""Sprint 3, user story 27: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint3, pytest.mark.story27]


def test_TC44_update_past_project_loads_and_saves_project_details(app, designer_client, past_project, project_data):
    invalid = designer_client.post(f'/designer/projects/past/{past_project}/update',
        json=dict(project_data, renovationCost=-1, description=' '))
    assert invalid.status_code == 400
    assert {'renovationCost', 'description'} <= invalid.json['errors'].keys()
    with app.app_context():
        unchanged = InteriorDesignProject.getPastProject(past_project)
        assert (unchanged.renovation_cost, unchanged.description) == (project_data['renovationCost'], project_data['description'])
    page = designer_client.get(f'/designer/projects/past/{past_project}/update')
    assert page.status_code == 200
    assert page.json['values']['projectName'] == 'Courtyard Retreat'
    values = dict(project_data, projectName='Updated Courtyard', description='Updated past project')
    response = designer_client.post(f'/designer/projects/past/{past_project}/update', json=values)
    assert response.status_code == 200
    with app.app_context():
        project = InteriorDesignProject.getPastProject(past_project)
        assert (project.project_name, project.description) == ('Updated Courtyard', 'Updated past project')
