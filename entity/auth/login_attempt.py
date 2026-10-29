import hashlib
from datetime import timedelta
from infrastructure.database import db
from infrastructure.time import utcnow


class LoginAttempt(db.Model):
    __tablename__ = 'login_attempt'
    attempt_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    @staticmethod
    def keyFor(username: str, remote_address: str = '') -> str:
        return hashlib.sha256(f'{remote_address}|{username.casefold()}'.encode()).hexdigest()

    @classmethod
    def isLimited(cls, key: str, attempt_limit: int) -> bool:
        count = db.session.scalar(db.select(db.func.count()).select_from(cls).where(
            cls.key == key, cls.created_at >= utcnow() - timedelta(minutes=15)))
        return count >= attempt_limit

    @classmethod
    def recordFailure(cls, key: str) -> None:
        db.session.add(cls(key=key))
        db.session.commit()

    @classmethod
    def clearFailures(cls, key: str) -> None:
        db.session.execute(db.delete(cls).where(cls.key == key))
        db.session.commit()
