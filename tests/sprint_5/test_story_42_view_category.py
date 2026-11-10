"""Sprint 5, user story 42: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story42]


def test_TC59_view_category_displays_saved_details(app, manager_client, category_id, category_data):
    # Invalid input passes through the controller and is rejected by the entity.
    from boundary.categories.view_category_page import ViewCategoryPage
    with app.test_request_context(headers={'Accept': 'application/json'}):
        boundary = ViewCategoryPage()
        boundary.onView('invalid')
        invalid = app.make_response(boundary.rendered_page)
    assert invalid.status_code == 400
    response = manager_client.get(f'/manager/categories/{category_id}')
    assert response.status_code == 200
    assert response.json['category'] == dict(category_data, categoryId=category_id, projectCount=0)
