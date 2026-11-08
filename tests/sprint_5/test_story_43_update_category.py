"""Sprint 5, user story 43: one successful workflow through BCE."""
import pytest
from entity.categories.category import Category

pytestmark = [pytest.mark.sprint5, pytest.mark.story43]


def test_update_category_loads_and_saves_category_details(app, manager_client, category_id, category_data):
    page = manager_client.get(f'/manager/categories/{category_id}/update')
    assert page.status_code == 200
    assert page.json['values']['categoryName'] == category_data['categoryName']
    response = manager_client.post(f'/manager/categories/{category_id}/update', json=dict(
        categoryName='Coastal', description='Light and open spaces.'))
    assert response.status_code == 200
    with app.app_context():
        category = Category.getCategory(category_id)
        assert (category.category_name, category.description) == ('Coastal', 'Light and open spaces.')
