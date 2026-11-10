"""Sprint 5, user story 42: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock

pytestmark = [pytest.mark.sprint5, pytest.mark.story42]


def test_view_category_displays_saved_details(app, manager_client, category_id, category_data, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.categories.view_category_page.ViewCategoryController.getCategory', blocked)
        from boundary.categories.view_category_page import ViewCategoryPage
        with app.test_request_context(headers={'Accept': 'application/json'}):
            boundary = ViewCategoryPage()
            boundary.onView('invalid')
            invalid = app.make_response(boundary.rendered_page)
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = manager_client.get(f'/manager/categories/{category_id}')
    assert response.status_code == 200
    assert response.json['category'] == dict(category_data, categoryId=category_id, projectCount=0)
