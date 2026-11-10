"""Sprint 2, user story 6: one successful workflow through BCE."""
import pytest
from entity.accounts.user_account import UserAccount

pytestmark = [pytest.mark.sprint2, pytest.mark.story6]


def test_TC23_create_user_account_saves_details_and_default_password(app, admin_client, seed_profile):
    profile_id = seed_profile('Customer')
    values = dict(username='customer1', full_name='Customer One', email='customer1@example.com',
                  phone_number='+65 6123 4567', profile_id=profile_id)
    with app.app_context():
        invalid = UserAccount()
        assert invalid.createUserAccount('bad_email', 'password', 'Bad Email', 'invalid', '+65 6123 4567', profile_id) is False
        assert 'email' in invalid.field_errors
    invalid_response = admin_client.post('/accounts/create', data=dict(values, email='invalid'))
    assert invalid_response.status_code == 400
    assert 'Enter a valid email address.' in invalid_response.text
    with app.app_context():
        assert UserAccount.getByUsername('customer1') is None
    response = admin_client.post('/accounts/create', data=values)
    assert response.status_code == 302
    with app.app_context():
        account = UserAccount.getByUsername('customer1')
        assert (account.full_name, account.email, account.phone_number, account.profile_id) == (
            values['full_name'], values['email'], values['phone_number'], profile_id)
        assert account.account_id and account.status == 'Active'
        assert account.has_password
        assert account.password_hash != 'password'
        assert account.check_password('password')
        assert not account.check_password('incorrect-password')
    login = app.test_client().post('/customer/login', json=dict(username='customer1', password='password'))
    assert login.status_code == 302
    assert login.location == '/customer'
    duplicate_username = admin_client.post('/accounts/create', data=dict(values, username='CUSTOMER1', email='different@example.com'))
    assert duplicate_username.status_code == 400
    duplicate_email = admin_client.post('/accounts/create', data=dict(values, username='customer2', email='CUSTOMER1@EXAMPLE.COM'))
    assert duplicate_email.status_code == 400
    with app.app_context():
        assert UserAccount.getByUsername('customer2') is None
