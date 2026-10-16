"""Non-destructive bridge from the profile-only project developed in the conversation."""
from sqlalchemy import inspect, text, Boolean
from flask import current_app
from infrastructure.database import db


def upgrade_database():
    from entity import models  # Register all tables.
    dialect = db.engine.dialect.name
    tables = inspect(db.engine).get_table_names()
    if 'user_profiles' in tables and 'user_profile' not in tables:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE user_profiles RENAME TO user_profile'))
        tables = inspect(db.engine).get_table_names()
    if 'user_profile' in tables:
        columns = {column['name']: column for column in inspect(db.engine).get_columns('user_profile')}
        required = {'profile_id', 'name', 'description', 'permissions'}
        if not required.issubset(columns):
            raise RuntimeError('The existing user_profile table has an unfamiliar structure. Back it up and review its columns before upgrading.')
        with db.engine.begin() as connection:
            if 'status' not in columns:
                connection.execute(text("ALTER TABLE user_profile ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Active'"))
                if dialect == 'postgresql':
                    connection.execute(text('ALTER TABLE user_profile ALTER COLUMN status DROP DEFAULT'))
            elif dialect == 'postgresql' and isinstance(columns['status']['type'], Boolean):
                connection.execute(text("ALTER TABLE user_profile ALTER COLUMN status DROP DEFAULT"))
                connection.execute(text("ALTER TABLE user_profile ALTER COLUMN status TYPE VARCHAR(20) USING CASE WHEN status THEN 'Active' ELSE 'Suspended' END"))
            duplicates = connection.execute(text('SELECT LOWER(name), COUNT(*) FROM user_profile GROUP BY LOWER(name) HAVING COUNT(*) > 1')).all()
            if duplicates:
                raise RuntimeError('Existing profiles have names that differ only by capitalisation. Rename the duplicates before upgrading; no profiles were deleted.')
    db.create_all()
    # create_all intentionally skips indexes for an already-existing table.
    with db.engine.begin() as connection:
        connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS uq_profile_name_lower ON user_profile (LOWER(name))'))
