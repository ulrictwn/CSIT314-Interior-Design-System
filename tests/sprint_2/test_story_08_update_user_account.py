"""Sprint 2, user story 8: one successful workflow through BCE."""
import pytest
from entity.accounts.user_account import UserAccount

pytestmark = [pytest.mark.sprint2, pytest.mark.story8]


def test_update_user_account_loads_and_saves_details(app, client, customer_account):
    page = client.get(f'/accounts/{customer_account}/update')
    assert page.status_code == 200
    assert 'customer1@example.com' in page.text
    with app.app_context():
        profile_id = UserAccount.getUserAccount(customer_account).profile_id
    response = client.post(f'/accounts/{customer_account}/update', data=dict(
        full_name='Updated Customer', email='updated@example.com', profile_id=profile_id))
    assert response.status_code == 302
    with app.app_context():
        account = UserAccount.getUserAccount(customer_account)
        assert (account.full_name, account.email, account.profile_id) == (
            'Updated Customer', 'updated@example.com', profile_id)
