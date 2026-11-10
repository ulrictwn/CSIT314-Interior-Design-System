"""Sprint 4, user story 31: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint4, pytest.mark.story31]


def test_TC48_customer_view_displays_project_details(app, customer_client, new_project, project_data):
    # Invalid input passes through the controller and is rejected by the entity.
    from boundary.customer.view_idp_page import ViewIDPPage
    with app.test_request_context(headers={'Accept': 'application/json'}):
        boundary = ViewIDPPage()
        boundary.onView('invalid')
        invalid = app.make_response(boundary.rendered_page)
    assert invalid.status_code == 400
    with app.app_context():
        assert InteriorDesignProject.getViewCount(new_project) == 0
    response = customer_client.get(f'/customer/projects/{new_project}')
    assert response.status_code == 200
    project = response.json['project']
    assert project['projectId'] == new_project
    for field, value in project_data.items():
        assert project[field] == value
