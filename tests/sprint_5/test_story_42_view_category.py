"""Sprint 5, user story 42: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story42]


def test_view_category_displays_saved_details(manager_client, category_id, category_data):
    response = manager_client.get(f'/manager/categories/{category_id}')
    assert response.status_code == 200
    assert response.json['category'] == dict(category_data, categoryId=category_id, projectCount=0)
