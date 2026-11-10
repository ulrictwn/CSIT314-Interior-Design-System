"""Business activity used by platform reports; saved in the caller's transaction."""
# infrastructure/database.py: the shared SQLAlchemy database connection.
from infrastructure.database import db
# infrastructure/time.py: UTC timestamp defaults.
from infrastructure.time import utcnow


class ActivityEvent(db.Model):
    __tablename__ = 'activity_event'

    event_id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.String(40), nullable=False, index=True)
    target_id = db.Column(db.String(32))
    occurred_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, index=True)
    # Creation-time category survives project reassignment/deletion and category deletion.
    category_id = db.Column(db.Integer)
    category_name = db.Column(db.String(100))

    @classmethod
    def record(cls, kind, target_id=None, category_id=None, category_name=None):
        """Add an activity record to the caller's database transaction."""
        db.session.add(cls(kind=kind, target_id=str(target_id) if target_id is not None else None,
                           category_id=category_id, category_name=category_name))
