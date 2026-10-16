"""Read existing account assignments without implementing account stories."""
from sqlalchemy import MetaData, Table, inspect
from infrastructure.database import db
from infrastructure.errors import DomainError


def profile_account_count(profile_id):
    connection = db.session.connection()
    existing = set(inspect(connection).get_table_names())
    total = 0
    for name in ('user_account', 'user_accounts'):
        if name not in existing:
            continue
        account = Table(name, MetaData(), autoload_with=connection)
        if 'profile_id' not in account.c:
            raise DomainError('The existing account table needs a profile_id assignment mapping before suspension is allowed.')
        total += db.session.scalar(db.select(db.func.count()).select_from(account).where(
            account.c.profile_id == profile_id))
    return total
