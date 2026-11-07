"""Basic diagram login/logout and the explicitly approved demo behavior."""
from unittest.mock import Mock
import re
import pytest
from flask import session

from boundary.auth.user_admin_login_page import UserAdminLoginPage
from boundary.auth.logout_page import LogoutPage
from control.auth.user_admin_login_controller import UserAdminLoginController
from entity.accounts.user_account import UserAccount
from infrastructure.database import db

PASSWORD = 'Review-Administrator-Password-123'


@pytest.mark.story11
def test_login_has_no_throttle_and_keeps_only_basic_account_state(app, admin_client):
    client = app.test_client()
    for _ in range(7):
        response = client.post('/login', data=dict(username='admin', password='Wrong-Password-123'))
        assert response.status_code == 400
        assert 'Invalid login details' in response.get_data(as_text=True)
    response = client.post('/login', data=dict(username='  admin  ', password=PASSWORD))
    assert response.status_code == 302 and response.headers['Location'] == '/dashboard'
    with client.session_transaction() as browser:
        assert browser['account_id'] == '101'
        assert 'session_token' not in browser and 'auth_version' not in browser
    assert 'Review Administrator' in client.get('/dashboard').get_data(as_text=True)


@pytest.mark.story11
def test_login_error_escapes_username_and_never_redisplays_password(app, admin_client):
    client = app.test_client()
    username = '<img src=x onerror=alert(1)>'
    password = 'Never-redisplay-this-Password-123'
    response = client.post('/login', data=dict(username=username, password=password))
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert username not in html and '&lt;img' in html
    assert password not in html
    assert 'value=' not in re.search(r'<input[^>]*name="password"[^>]*>', html).group(0)


@pytest.mark.story11
def test_login_controller_relays_boolean_result_and_account(app, admin_client):
    with app.app_context():
        controller = UserAdminLoginController()
        assert controller.login('admin', 'Wrong-Password-123') is False
        assert controller.account is None and controller.error_message == 'Invalid login details'
        assert controller.login('admin', PASSWORD) is True
        assert controller.account.username == 'admin' and controller.error_message is None


@pytest.mark.story11
@pytest.mark.story12
@pytest.mark.parametrize('valid', [True, False])
def test_boundary_events_are_void_and_prepare_http_responses(app, admin_client, valid):
    password = PASSWORD if valid else 'Wrong-Password-123'
    with app.test_request_context('/login', method='POST', data=dict(username='admin', password=password)):
        page = UserAdminLoginPage()
        assert page.onLogin('admin', password) is None
        if valid:
            assert page.rendered_page.status_code == 302 and session['account_id'] == '101'
            logout_page = LogoutPage()
            assert logout_page.logout() is None
            assert 'account_id' not in session
            assert logout_page.rendered_page.headers['Location'] == '/login'
        else:
            assert page.rendered_page[1] == 400
            assert 'Invalid login details' in page.rendered_page[0]
            assert 'account_id' not in session
