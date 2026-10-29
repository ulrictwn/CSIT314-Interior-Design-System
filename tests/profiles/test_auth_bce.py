"""Authentication behavior across the BCE layers and real CSRF-protected routes."""
import hashlib
import re
from datetime import timedelta, timezone
from urllib.parse import quote

import pytest
from flask import session

from boundary.auth.login_page import LoginPage
from boundary.auth.logout_page import LogoutPage
from entity.accounts.user_account import UserAccount
from entity.auth.login_attempt import LoginAttempt
from entity.auth.login_session import LoginSession
from entity.profile.user_profile import UserProfile
from infrastructure.database import db
from infrastructure.time import utcnow

pytestmark = pytest.mark.security
PASSWORD = 'Review-Administrator-Password-123'


def csrf(client, path='/login'):
    response = client.get(path)
    assert response.status_code == 200
    return re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.get_data(as_text=True)).group(1)


def login(client, username='admin', password=PASSWORD, *, address='127.0.0.1', target='/login'):
    return client.post(target, data=dict(username=username, password=password, csrf_token=csrf(client)),
                       environ_overrides={'REMOTE_ADDR': address})


@pytest.mark.story11
def test_rate_limit_uses_normalized_username_address_and_configuration(app, admin_client):
    app.config['LOGIN_ATTEMPT_LIMIT'] = 2
    client = app.test_client()
    for username in [' AdMiN ', 'admin']:
        response = login(client, username, 'Wrong-Password-123')
        assert response.status_code == 400
        assert 'Invalid login details' in response.get_data(as_text=True)
    response = login(client)
    assert response.status_code == 400
    assert 'Too many unsuccessful attempts' in response.get_data(as_text=True)
    assert login(app.test_client(), address='192.0.2.1').status_code == 302
    response = login(app.test_client(), 'missing-admin')
    assert response.status_code == 400
    assert 'Invalid login details' in response.get_data(as_text=True)
    with app.app_context():
        key = LoginAttempt.keyFor('admin', '127.0.0.1')
        attempts = db.session.scalars(db.select(LoginAttempt).where(LoginAttempt.key == key)).all()
        assert len(attempts) == 2
        # One old failure and one recent failure are below the configured limit.
        attempts[0].created_at = utcnow() - timedelta(minutes=15, seconds=1)
        db.session.commit()
    assert login(client).status_code == 302
    with app.app_context():
        assert not db.session.scalar(db.select(db.func.count()).select_from(LoginAttempt).where(LoginAttempt.key == key))
        assert db.session.scalar(db.select(db.func.count()).select_from(LoginAttempt)) == 1


@pytest.mark.story11
def test_fifteen_minute_window_includes_the_exact_boundary(app, admin_client, monkeypatch):
    now = utcnow()
    monkeypatch.setattr('entity.auth.login_attempt.utcnow', lambda: now)
    app.config['LOGIN_ATTEMPT_LIMIT'] = 1
    key = LoginAttempt.keyFor('admin', '127.0.0.1')
    with app.app_context():
        attempt = LoginAttempt(key=key, created_at=now - timedelta(minutes=15))
        db.session.add(attempt)
        db.session.commit()
    response = login(app.test_client())
    assert response.status_code == 400
    assert 'Too many unsuccessful attempts' in response.get_data(as_text=True)
    with app.app_context():
        attempt = db.session.scalar(db.select(LoginAttempt).where(LoginAttempt.key == key))
        attempt.created_at = now - timedelta(minutes=15, microseconds=1)
        db.session.commit()
    assert login(app.test_client()).status_code == 302


@pytest.mark.story11
def test_browser_receives_token_but_database_stores_only_its_hash(app, admin_client, sign_in):
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=7)
    before = utcnow()
    client, response = sign_in('admin')
    after = utcnow()
    assert response.status_code == 302
    with client.session_transaction() as browser:
        assert browser.permanent is True
        token, account_id = browser['session_token'], browser['account_id']
    digest = hashlib.sha256(token.encode()).hexdigest()
    with app.app_context():
        record = db.session.get(LoginSession, digest)
        assert record is not None and record.account_id == account_id
        assert record.token_hash != token
        expires = record.expires_at.replace(tzinfo=timezone.utc)
        assert before + timedelta(minutes=7) <= expires <= after + timedelta(minutes=7)
        assert db.session.get(LoginSession, token) is None


@pytest.mark.story11
def test_logging_in_again_rotates_current_token_and_keeps_other_browser(app, admin_client, sign_in):
    client, response = sign_in('admin')
    assert response.status_code == 302
    previous_cookie = client.get_cookie('session').value
    with client.session_transaction() as browser:
        previous_token = browser['session_token']
    response = client.post('/login', data=dict(username='admin', password=PASSWORD,
                                               csrf_token=csrf(client, '/dashboard')))
    assert response.status_code == 302
    with client.session_transaction() as browser:
        current_token = browser['session_token']
    assert current_token != previous_token
    with app.app_context():
        assert db.session.get(LoginSession, LoginSession.tokenHash(previous_token)) is None
        assert db.session.get(LoginSession, LoginSession.tokenHash(current_token)) is not None
    replay = app.test_client()
    replay.set_cookie('session', previous_cookie)
    assert replay.get('/dashboard').status_code == 403
    assert client.get('/dashboard').status_code == 200
    assert admin_client.get('/dashboard').status_code == 200


@pytest.mark.story11
@pytest.mark.parametrize('change', ['expired', 'version', 'missing-token', 'forged-token',
                                   'unknown-account', 'suspended-account', 'suspended-profile', 'changed-role'])
def test_session_loader_rejects_invalid_or_unavailable_sessions(app, admin_client, sign_in, change):
    client, response = sign_in('admin')
    assert response.status_code == 302
    with client.session_transaction() as browser:
        token, account_id = browser['session_token'], browser['account_id']
        if change == 'missing-token':
            browser.pop('session_token')
        elif change == 'forged-token':
            browser['session_token'] = 'forged-token'
        elif change == 'unknown-account':
            browser['account_id'] = 'missing-account'
    with app.app_context():
        account = db.session.get(UserAccount, account_id)
        if change == 'expired':
            db.session.get(LoginSession, LoginSession.tokenHash(token)).expires_at = utcnow() - timedelta(seconds=1)
        elif change == 'version':
            account.auth_version += 1
        elif change == 'suspended-account':
            account.status = 'Suspended'
        elif change == 'suspended-profile':
            account.profile.status = 'Suspended'
        elif change == 'changed-role':
            account.profile_id = UserProfile.getProfile('Customer').profile_id
        db.session.commit()
    assert client.get('/dashboard').status_code == 403
    with client.session_transaction() as browser:
        assert not {'account_id', 'session_token', 'auth_version'}.intersection(browser)


@pytest.mark.story11
@pytest.mark.parametrize('submitted_token', [None, 'forged-token'])
def test_plain_login_form_rejects_missing_or_forged_csrf_without_auth_changes(app, admin_client, submitted_token):
    client = app.test_client()
    csrf(client)
    data = dict(username='admin', password=PASSWORD)
    if submitted_token:
        data['csrf_token'] = submitted_token
    response = client.post('/login', data=data)
    assert response.status_code == 400
    assert 'form security token is missing or expired' in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(LoginSession)) == 1
        assert db.session.scalar(db.select(db.func.count()).select_from(LoginAttempt)) == 0
    assert client.get('/dashboard').status_code == 403


@pytest.mark.story12
@pytest.mark.parametrize('submitted_token', [None, 'forged-token'])
def test_plain_logout_form_rejects_missing_or_forged_csrf_and_keeps_session(app, admin_client, submitted_token):
    with admin_client.session_transaction() as browser:
        token = browser['session_token']
    data = dict(csrf_token=submitted_token) if submitted_token else {}
    assert admin_client.post('/logout', data=data).status_code == 400
    assert admin_client.get('/dashboard').status_code == 200
    with app.app_context():
        assert db.session.get(LoginSession, LoginSession.tokenHash(token)) is not None


@pytest.mark.story11
@pytest.mark.parametrize('destination,expected', [
    ('/accounts/search?username=admin', '/accounts/search?username=admin'),
    ('https://example.com/collect', '/dashboard'), ('//example.com/collect', '/dashboard'),
    ('/\\example.com/collect', '/dashboard'), ('/dashboard\n', '/dashboard'),
    ('relative-path', '/dashboard'),
])
def test_login_redirects_only_to_safe_internal_destinations(app, admin_client, destination, expected):
    response = login(app.test_client(), target='/login?next=' + quote(destination, safe=''))
    assert response.status_code == 302
    assert response.headers['Location'] == expected


@pytest.mark.story11
def test_login_error_escapes_username_and_never_redisplays_password(app, admin_client):
    username = '<img src=x onerror=alert(1)>'
    password = 'Never-redisplay-this-Password-123'
    response = login(app.test_client(), username, password)
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert username not in html and '&lt;img' in html
    assert password not in html
    password_input = re.search(r'<input[^>]*name="password"[^>]*>', html).group(0)
    assert 'value=' not in password_input


@pytest.mark.story12
def test_logout_remains_post_only(admin_client):
    assert admin_client.get('/logout').status_code == 405
    assert admin_client.get('/dashboard').status_code == 200


@pytest.mark.story11
@pytest.mark.story12
@pytest.mark.parametrize('valid', [True, False])
def test_boundary_events_are_void_and_prepare_http_responses(app, admin_client, valid):
    password = PASSWORD if valid else 'Wrong-Password-123'
    with app.test_request_context('/login', method='POST', data=dict(username='admin', password=password)):
        page = LoginPage()
        assert page.clickLogin('admin', password) is None
        if valid:
            assert page.rendered_page.status_code == 302
            assert 'session_token' in session
            logout_page = LogoutPage()
            assert logout_page.logout() is None
            assert 'session_token' not in session
            assert logout_page.rendered_page.status_code == 302
            assert logout_page.rendered_page.headers['Location'] == '/login'
        else:
            assert page.rendered_page[1] == 400
            assert 'Invalid login details' in page.rendered_page[0]
            assert 'session_token' not in session
