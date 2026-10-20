from infrastructure.database import db
from infrastructure.time import utcnow


class LoginAttempt(db.Model):
    __tablename__ = 'login_attempt'
    attempt_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
