"""Sprint 5, user story 45: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story45]


def test_search_categories_returns_matching_category(client, category_id):
    response = client.get('/manager/categories/search', query_string={'q': 'Japandi'})
    assert response.status_code == 200
    assert [category['categoryId'] for category in response.json['categories']] == [category_id]
