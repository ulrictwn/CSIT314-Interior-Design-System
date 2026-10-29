from sqlalchemy.exc import IntegrityError
from infrastructure.database import db
from infrastructure.errors import DomainError


def save(record, message='A record with these details already exists.'):
    try:
        db.session.add(record)
        db.session.commit()
        return record
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError(message) from exc


def remove(record):
    try:
        db.session.delete(record)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError('This record is still in use and cannot be deleted.') from exc
