"""Sprint 3, user story 26: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story26]


def test_view_past_project_displays_saved_details(designer_client, past_project, designer_account, project_data):
    response = designer_client.get(f'/designer/projects/past/{past_project}')
    assert response.status_code == 200
    expected = dict(project_data, projectName='Courtyard Retreat', projectId=past_project,
                    accountId=designer_account, status='Past')
    assert response.json['project'] == expected
