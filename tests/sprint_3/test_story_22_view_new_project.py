"""Sprint 3, user story 22: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story22]


def test_view_new_project_displays_saved_details(designer_client, new_project, designer_account, project_data):
    response = designer_client.get(f'/designer/projects/new/{new_project}')
    assert response.status_code == 200
    assert response.json['project'] == dict(project_data, projectId=new_project, accountId=designer_account, status='New')
