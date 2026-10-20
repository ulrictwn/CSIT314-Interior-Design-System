import hashlib
from datetime import timedelta
from flask import current_app
from entity.user_account import UserAccount
from entity.login_attempt import LoginAttempt
from entity.login_session import LoginSession
from infrastructure.auth import token_hash
from infrastructure.database import db
from infrastructure.time import utcnow
from infrastructure.errors import DomainError


class LoginController:
    def login(self, username, password, remote_address=''):
        if not isinstance(username, str) or not username.strip() or len(username) > 80 or not isinstance(password, str) or not password or len(password) > 128:
            raise DomainError('Invalid login details')
        username = username.strip()
        key = hashlib.sha256(f'{remote_address}|{username.casefold()}'.encode()).hexdigest()
        count = db.session.scalar(db.select(db.func.count()).select_from(LoginAttempt).where(
            LoginAttempt.key == key, LoginAttempt.created_at >= utcnow() - timedelta(minutes=15)))
        if count >= current_app.config['LOGIN_ATTEMPT_LIMIT']:
            raise DomainError('Too many unsuccessful attempts. Try again in 15 minutes.')
        if not UserAccount.login(username, password):
            db.session.add(LoginAttempt(key=key))
            db.session.commit()
            raise DomainError('Invalid login details')
        self.account = UserAccount.getByUsername(username)
        db.session.execute(db.delete(LoginAttempt).where(LoginAttempt.key == key))
        db.session.commit()
        return True


class LogoutController:
    def logout(self, user_session):
        token = user_session.get('session_token')
        if isinstance(token, str):
            db.session.execute(db.delete(LoginSession).where(LoginSession.token_hash == token_hash(token)))
            db.session.commit()
        user_session.clear()
