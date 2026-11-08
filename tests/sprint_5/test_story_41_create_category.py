"""Sprint 5, user story 41: one successful workflow through BCE."""
import pytest
from entity.categories.category import Category

pytestmark = [pytest.mark.sprint5, pytest.mark.story41]


def test_create_category_saves_category_details(app, client, category_data):
    response = client.post('/manager/categories/create', json=category_data)
    assert response.status_code == 201
    category_id = response.json['category']['categoryId']
    with app.app_context():
        category = Category.getCategory(category_id)
        assert (category.category_name, category.description) == (
            category_data['categoryName'], category_data['description'])
