"""Sprint 5, user story 44: one successful workflow through BCE."""
import pytest
from entity.categories.category import Category

pytestmark = [pytest.mark.sprint5, pytest.mark.story44]


def test_TC61_delete_category_removes_saved_category(app, manager_client, category_id):
    # Invalid input passes through the controller and is rejected by the entity.
    from boundary.categories.delete_category_page import DeleteCategoryPage
    with app.test_request_context(headers={'Accept': 'application/json'}):
        boundary = DeleteCategoryPage()
        boundary.onDelete('invalid')
        invalid = app.make_response(boundary.rendered_page)
    assert invalid.status_code == 400
    with app.app_context():
        assert Category.getCategory(category_id) is not None
    confirmation = manager_client.get(f'/manager/categories/{category_id}/delete')
    assert confirmation.status_code == 200
    assert confirmation.json['confirmationRequired'] is True
    response = manager_client.post(f'/manager/categories/{category_id}/delete')
    assert response.status_code == 200
    with app.app_context():
        assert Category.getCategory(category_id) is None
