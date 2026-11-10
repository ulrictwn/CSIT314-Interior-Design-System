"""Sprint 5, user story 41: one successful workflow through BCE."""
import pytest
from entity.categories.category import Category

pytestmark = [pytest.mark.sprint5, pytest.mark.story41]


def test_TC58_create_category_saves_category_details(app, manager_client, category_data):
    # Invalid input passes through the controller and is rejected by the entity.
    invalid = manager_client.post('/manager/categories/create', json={'categoryName': '  Valid name  ', 'description': ''})
    assert invalid.status_code == 400
    assert invalid.json['values'] == dict(categoryName='Valid name', description='')
    assert 'description' in invalid.json['errors']
    with app.app_context():
        assert Category.searchCategories('') == []
    response = manager_client.post('/manager/categories/create', json=category_data)
    assert response.status_code == 201
    category_id = response.json['category']['categoryId']
    with app.app_context():
        category = Category.getCategory(category_id)
        assert (category.category_name, category.description) == (
            category_data['categoryName'], category_data['description'])
    duplicate = manager_client.post('/manager/categories/create', json=dict(
        category_data, categoryName=category_data['categoryName'].upper()))
    assert duplicate.status_code == 400
    assert 'categoryName' in duplicate.json['errors']
