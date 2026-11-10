"""Sprint 4, user story 30: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint4, pytest.mark.story30]


def test_TC47_customer_search_returns_matching_project(app, customer_client, new_project, past_project, project_data):
    # Invalid input passes through the controller and is rejected by the entity.
    invalid = customer_client.post('/customer/projects', json={'keyword': ['invalid']})
    assert invalid.status_code == 400
    assert 'keyword' in invalid.json['errors']
    with app.app_context():
        assert InteriorDesignProject().updateNewProject(new_project,
            **dict(project_data, projectName='Updated Seaside Home'))
    response = customer_client.get('/customer/projects', query_string={'q': 'Seaside'})
    assert response.status_code == 200
    assert [project['projectId'] for project in response.json['projects']] == [new_project]
    assert response.json['projects'][0]['projectName'] == 'Updated Seaside Home'
