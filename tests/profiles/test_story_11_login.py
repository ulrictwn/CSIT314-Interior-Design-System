import pytest
from infrastructure.database import db
from entity.accounts.user_account import UserAccount
pytestmark=pytest.mark.story11

def test_TC37_valid_admin_login_opens_dashboard(admin_client):
    response=admin_client.get('/dashboard')
    assert response.status_code==200
    assert 'Review Administrator' in response.get_data(as_text=True)

@pytest.mark.parametrize('failure',['password','username','nonadmin','suspended-account','suspended-profile'])
def test_T38_invalid_or_unavailable_admin_login_is_generic(app,create_account,set_account_password,sign_in,failure):
    create_account('customer1')
    create_account('secondadmin','User Admin')
    set_account_password('customer1')
    set_account_password('secondadmin')
    username,password='secondadmin','Review-Administrator-Password-123'
    if failure=='password':password='Incorrect-Password-123'
    if failure=='username':username='missing-user'
    if failure=='nonadmin':username='customer1'
    with app.app_context():
        if failure=='suspended-account':UserAccount.getByUsername('secondadmin').status='Suspended'
        if failure=='suspended-profile':UserAccount.getByUsername('secondadmin').profile.status='Suspended'
        db.session.commit()
    client,response=sign_in(username,password)
    assert response.status_code==400
    assert 'Invalid login details' in response.get_data(as_text=True)
    assert client.get('/dashboard').status_code==403



@pytest.mark.parametrize('username,password', [
    (None, 'Password-123456'), ('', 'Password-123456'),
    ('   ', 'Password-123456'), ('x' * 81, 'Password-123456'),
    ('admin', None), ('admin', ''), ('admin', 'x' * 129),
    ('admin', ' ' * 12), (123, 'Password-123456'), ('admin', []),
])
def test_malformed_credentials_are_rejected_by_entity_before_database_access(monkeypatch, username, password):
    from unittest.mock import Mock
    from control.auth.login_controller import LoginController
    from infrastructure.errors import DomainError

    query = Mock(side_effect=AssertionError('Invalid credentials reached the database'))
    monkeypatch.setattr(db.session, 'execute', query)
    assert UserAccount().login(username, password) is False
    with pytest.raises(DomainError, match='Invalid login details'):
        UserAccount.validateLoginCredentials(username, password)
    controller = LoginController()
    assert controller.login(username, password) is False
    assert controller.error_message == 'Invalid login details'
    query.assert_not_called()


def test_credential_validation_preserves_normalization_and_length_boundaries():
    assert UserAccount.validateLoginCredentials('  admin  ', ' Password-123456 ') == 'admin'
    assert UserAccount.validateLoginCredentials('a' * 80, 'p' * 128) == 'a' * 80


def test_entity_login_keeps_password_whitespace_significant(app, seed):
    profile_id = seed('User Admin')
    password = '  Valid-Password-123  '
    with app.app_context():
        account = UserAccount()
        assert account.createUserAccount('spaceadmin', 'Space Admin', 'space@example.com',
            '+65 6123 4567', profile_id, password=password) is True
        assert UserAccount().login('  spaceadmin  ', password) is True
        assert UserAccount().login('spaceadmin', password.strip()) is False
