"""Sprint 2, user story 6: one successful workflow through BCE."""
import pytest
from entity.accounts.user_account import UserAccount

pytestmark = [pytest.mark.sprint2, pytest.mark.story6]


def test_create_user_account_saves_details_without_password(app, client, seed_profile):
    profile_id = seed_profile('Customer')
    values = dict(username='customer1', full_name='Customer One', email='customer1@example.com',
                  phone_number='+65 6123 4567', profile_id=profile_id)
    response = client.post('/accounts/create', data=values)
    assert response.status_code == 302
    with app.app_context():
        account = UserAccount.getByUsername('customer1')
        assert (account.full_name, account.email, account.phone_number, account.profile_id) == (
            values['full_name'], values['email'], values['phone_number'], profile_id)
        assert account.account_id and account.status == 'Active'
        assert not account.has_password
