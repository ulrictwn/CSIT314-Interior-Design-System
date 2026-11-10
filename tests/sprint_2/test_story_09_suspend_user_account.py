"""Sprint 2, user story 9: one successful workflow through BCE."""
import pytest
from entity.accounts.user_account import UserAccount

pytestmark = [pytest.mark.sprint2, pytest.mark.story9]


def test_TC26_suspend_user_account_saves_suspended_status(app, admin_client, customer_account):
    response = admin_client.post(f'/accounts/{customer_account}/suspend')
    assert response.status_code == 302
    with app.app_context():
        assert UserAccount.getUserAccount(customer_account).status == 'Suspended'
