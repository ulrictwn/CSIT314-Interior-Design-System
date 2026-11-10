"""Sprint 4, user story 31: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock

pytestmark = [pytest.mark.sprint4, pytest.mark.story31]


def test_customer_view_displays_project_details(app, customer_client, new_project, project_data, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.customer.view_idp_page.ViewIDPController.getIDP', blocked)
        from boundary.customer.view_idp_page import ViewIDPPage
        with app.test_request_context(headers={'Accept': 'application/json'}):
            boundary = ViewIDPPage()
            boundary.onView('invalid')
            invalid = app.make_response(boundary.rendered_page)
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = customer_client.get(f'/customer/projects/{new_project}')
    assert response.status_code == 200
    project = response.json['project']
    assert project['projectId'] == new_project
    for field, value in project_data.items():
        assert project[field] == value
