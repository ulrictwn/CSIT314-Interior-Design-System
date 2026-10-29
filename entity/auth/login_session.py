import hashlib
import secrets
from datetime import timedelta
from infrastructure.database import db
from infrastructure.time import utcnow


class LoginSession(db.Model):
    __tablename__ = 'login_session'
    token_hash = db.Column(db.String(64), primary_key=True)
    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='CASCADE'), nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    @staticmethod
    def tokenHash(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def start(cls, account, lifetime: timedelta, *, previous_token=None) -> dict:
        if isinstance(previous_token, str):
            db.session.execute(db.delete(cls).where(cls.token_hash == cls.tokenHash(previous_token)))
        token = secrets.token_urlsafe(32)
        db.session.add(cls(token_hash=cls.tokenHash(token), account_id=account.account_id,
            expires_at=utcnow() + lifetime))
        db.session.commit()
        return dict(account_id=account.account_id, auth_version=account.auth_version, session_token=token)

    @classmethod
    def getAuthenticatedAccount(cls, account_id, token, auth_version):
        from entity.accounts.user_account import UserAccount
        account = db.session.get(UserAccount, account_id)
        record = None
        if isinstance(token, str):
            record = db.session.execute(db.select(cls).where(
                cls.token_hash == cls.tokenHash(token), cls.account_id == account_id,
                cls.expires_at > utcnow())).scalar_one_or_none()
        if account and record and account.active and account.is_admin and auth_version == account.auth_version:
            return account
        return None

    @classmethod
    def revoke(cls, token) -> None:
        if isinstance(token, str):
            db.session.execute(db.delete(cls).where(cls.token_hash == cls.tokenHash(token)))
            db.session.commit()
