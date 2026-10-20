from infrastructure.database import db
from infrastructure.time import utcnow


class LoginSession(db.Model):
    __tablename__ = 'login_session'
    token_hash = db.Column(db.String(64), primary_key=True)
    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='CASCADE'), nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
