"""Sprint 2, user story 7: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story7]


def test_view_user_account_displays_saved_details(admin_client, customer_account):
    response = admin_client.get(f'/accounts/{customer_account}')
    assert response.status_code == 200
    for value in (customer_account, 'customer1', 'Name customer1', 'customer1@example.com',
                  '+65 6123 4567', 'Customer', 'Active'):
        assert value in response.text
