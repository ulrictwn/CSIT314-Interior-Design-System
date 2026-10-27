import pytest

from entity.user_account import UserAccount
from entity.user_profile import UserProfile

pytestmark = pytest.mark.story6


def test_TC77_create_form_has_details_and_no_password_fields(admin_client):
    response = admin_client.get('/accounts/create')
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    for name in ('username', 'full_name', 'email', 'phone_number', 'profile_id', 'csrf_token'):
        assert f'name="{name}"' in html
    assert 'name="password"' not in html
    assert 'name="confirm_password"' not in html


def test_TC78_password_free_admin_cannot_sign_in_until_password_is_set(app, create_account, sign_in):
    account_id = create_account('newadmin', 'User Admin')
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        assert account.status == 'Active' and not account.has_password
        assert not UserAccount.login('newadmin', 'not-an-actual-account-password')
    client, response = sign_in('newadmin')
    assert response.status_code == 400
    assert 'Invalid login details' in response.get_data(as_text=True)
    assert client.get('/dashboard').status_code == 403


def test_TC79_submitted_password_fields_cannot_set_credentials(app, admin_client, submit):
    with app.app_context():
        profile_id = UserProfile.getProfile('User Admin').profile_id
    response = submit('/accounts/create', dict(username='newadmin', full_name='New Admin',
        email='newadmin@example.com', phone_number='+65 6123 4567', profile_id=profile_id,
        password='Injected-Password-123', confirm_password='Injected-Password-123'))
    assert response.status_code == 302
    with app.app_context():
        assert not UserAccount.getByUsername('newadmin').has_password
        assert not UserAccount.login('newadmin', 'Injected-Password-123')


def test_TC80_admin_without_password_cannot_replace_last_usable_admin(app, create_account, submit):
    create_account('newadmin', 'User Admin')
    with app.app_context():
        profile_id = UserProfile.getProfile('Customer').profile_id
    response = submit('/accounts/101/update', dict(full_name='Original Admin',
        email='admin@example.com', profile_id=profile_id))
    assert response.status_code == 400
    assert 'Keep at least one active User Admin' in response.get_data(as_text=True)
    with app.app_context():
        assert UserAccount.getByUsername('admin').is_admin


def test_TC81_setting_password_enables_login_and_provides_another_usable_admin(
        app, admin_client, create_account, set_account_password, sign_in, submit):
    create_account('newadmin', 'User Admin')
    set_account_password('newadmin')
    other, response = sign_in('newadmin')
    assert response.status_code == 302 and other.get('/dashboard').status_code == 200
    with app.app_context():
        account = UserAccount.getByUsername('newadmin')
        assert account.has_password and account.check_password('Review-Administrator-Password-123')
        profile_id = UserProfile.getProfile('Customer').profile_id
    response = submit('/accounts/101/update', dict(full_name='Original Admin',
        email='admin@example.com', profile_id=profile_id))
    assert response.status_code == 302
    assert admin_client.get('/dashboard').status_code == 403
    assert other.get('/dashboard').status_code == 200
