import hashlib
import secrets
from urllib.parse import urlsplit
from flask import current_app, g, session, url_for
from entity.user_account import UserAccount
from entity.login_session import LoginSession
from infrastructure.database import db
from infrastructure.time import utcnow


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


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
    account = db.session.get(UserAccount, account_id)
    record = None
    if isinstance(token, str):
        record = db.session.execute(db.select(LoginSession).where(
            LoginSession.token_hash == token_hash(token), LoginSession.account_id == account_id,
            LoginSession.expires_at > utcnow())).scalar_one_or_none()
    if account and record and account.active and account.is_admin and session.get('auth_version') == account.auth_version:
        g.current_user = g.profile_actor = account
    else:
        session.clear()


def establish_session(account):
    old_token = session.get('session_token')
    if isinstance(old_token, str):
        db.session.execute(db.delete(LoginSession).where(LoginSession.token_hash == token_hash(old_token)))
    token = secrets.token_urlsafe(32)
    db.session.add(LoginSession(token_hash=token_hash(token), account_id=account.account_id,
        expires_at=utcnow() + current_app.permanent_session_lifetime))
    db.session.commit()
    session.clear()
    session['account_id'], session['auth_version'], session['session_token'] = account.account_id, account.auth_version, token
    session.permanent = True


def safe_next(value):
    if isinstance(value, str) and value.startswith('/') and not value.startswith('//') and '\\' not in value:
        parsed = urlsplit(value)
        if not parsed.scheme and not parsed.netloc and not any(ord(c) < 32 for c in value):
            return value
    return url_for('dashboard')
