"""Business activity used by platform reports; saved in the caller's transaction."""
from infrastructure.database import db
from infrastructure.time import utcnow


class ActivityEvent(db.Model):
    __tablename__ = 'activity_event'

    event_id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40), nullable=False, index=True)
    target_id = db.Column(db.String(32))
    occurred_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    @classmethod
    def record(cls, kind, target_id=None):
        db.session.add(cls(kind=kind, target_id=str(target_id) if target_id is not None else None))
