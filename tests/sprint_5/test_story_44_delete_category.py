"""Sprint 5, user story 44: one successful workflow through BCE."""
import pytest
from entity.categories.category import Category

pytestmark = [pytest.mark.sprint5, pytest.mark.story44]


def test_delete_category_removes_saved_category(app, manager_client, category_id):
    confirmation = manager_client.get(f'/manager/categories/{category_id}/delete')
    assert confirmation.status_code == 200
    assert confirmation.json['confirmationRequired'] is True
    response = manager_client.post(f'/manager/categories/{category_id}/delete')
    assert response.status_code == 200
    with app.app_context():
        assert Category.getCategory(category_id) is None
