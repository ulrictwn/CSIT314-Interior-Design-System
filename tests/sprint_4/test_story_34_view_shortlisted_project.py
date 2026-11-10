"""Sprint 4, user story 34: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject

pytestmark = [pytest.mark.sprint4, pytest.mark.story34]


def test_TC51_customer_views_saved_project_details(app, customer_client, customer_account, saved_project, project_data):
    # Invalid input passes through the controller and is rejected by the entity.
    from boundary.customer.view_shortlist_idp_page import ViewShortlistIDPPage
    with app.test_request_context(headers={'Accept': 'application/json'}):
        boundary = ViewShortlistIDPPage()
        boundary.onView('invalid')
        invalid = app.make_response(boundary.rendered_page)
    assert invalid.status_code == 400
    with app.app_context():
        assert InteriorDesignProject.getViewCount(saved_project) == 0
    response = customer_client.get(f'/customer/shortlist/{saved_project}', query_string={'accountId': customer_account})
    assert response.status_code == 200
    project = response.json['project']
    assert project['projectId'] == saved_project
    for field, value in project_data.items():
        assert project[field] == value
