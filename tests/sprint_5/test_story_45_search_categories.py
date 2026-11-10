"""Sprint 5, user story 45: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story45]


def test_TC62_search_categories_returns_matching_category(manager_client, category_id):
    # Invalid input passes through the controller and is rejected by the entity.
    invalid = manager_client.post('/manager/categories/search', json={'keyword': 'x' * 201})
    assert invalid.status_code == 400
    assert 'keyword' in invalid.json['errors']
    response = manager_client.get('/manager/categories/search', query_string={'q': 'Japandi'})
    assert response.status_code == 200
    assert [category['categoryId'] for category in response.json['categories']] == [category_id]
