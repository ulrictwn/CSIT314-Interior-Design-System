"""Sprint 5, user story 44: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock
from entity.categories.category import Category

pytestmark = [pytest.mark.sprint5, pytest.mark.story44]


def test_delete_category_removes_saved_category(app, manager_client, category_id, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.categories.delete_category_page.DeleteCategoryController.deleteCategory', blocked)
        from boundary.categories.delete_category_page import DeleteCategoryPage
        with app.test_request_context(headers={'Accept': 'application/json'}):
            boundary = DeleteCategoryPage()
            boundary.onDelete('invalid')
            invalid = app.make_response(boundary.rendered_page)
        assert invalid.status_code == 400
        blocked.assert_not_called()
    confirmation = manager_client.get(f'/manager/categories/{category_id}/delete')
    assert confirmation.status_code == 200
    assert confirmation.json['confirmationRequired'] is True
    response = manager_client.post(f'/manager/categories/{category_id}/delete')
    assert response.status_code == 200
    with app.app_context():
        assert Category.getCategory(category_id) is None
