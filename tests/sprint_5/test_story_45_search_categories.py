"""Sprint 5, user story 45: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock

pytestmark = [pytest.mark.sprint5, pytest.mark.story45]


def test_search_categories_returns_matching_category(manager_client, category_id, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.categories.search_category_page.SearchCategoryController.searchCategories', blocked)
        invalid = manager_client.post('/manager/categories/search', json={'keyword': 'x' * 201})
        assert invalid.status_code == 400
        blocked.assert_not_called()
    response = manager_client.get('/manager/categories/search', query_string={'q': 'Japandi'})
    assert response.status_code == 200
    assert [category['categoryId'] for category in response.json['categories']] == [category_id]
