from urllib.parse import urlsplit
from flask import current_app, g, session, url_for
from entity.auth.login_session import LoginSession


def load_account():
    g.current_user = g.profile_actor = None
    # Compatibility with the existing isolated profile tests; never a web login bypass.
    if current_app.testing:
        loader = current_app.config.get('PROFILE_ACTOR_LOADER')
        if loader:
            g.profile_actor = loader()
            return
        if current_app.config.get('PROFILE_DEVELOPMENT_PREVIEW'):
            from app import DevelopmentProfileActor
            g.profile_actor = DevelopmentProfileActor()
            return
    account_id, token = session.get('account_id'), session.get('session_token')
    if not account_id:
        return
    account = LoginSession.getAuthenticatedAccount(account_id, token, session.get('auth_version'))
    if account:
        g.current_user = g.profile_actor = account
    else:
        session.clear()


def safe_next(value):
    if isinstance(value, str) and value.startswith('/') and not value.startswith('//') and '\\' not in value:
        parsed = urlsplit(value)
        if not parsed.scheme and not parsed.netloc and not any(ord(c) < 32 for c in value):
            return value
    return url_for('dashboard')
