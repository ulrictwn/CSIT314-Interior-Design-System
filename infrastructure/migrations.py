"""Non-destructive bridge from the profile-only project developed in the conversation."""
from sqlalchemy import inspect, text, Boolean
from flask import current_app
from infrastructure.database import db


def upgrade_database():
    from entity import models  # Register all tables.
    dialect = db.engine.dialect.name
    tables = inspect(db.engine).get_table_names()
    if 'user_account' in tables:
        columns = {column['name']: column for column in inspect(db.engine).get_columns('user_account')}
        from sqlalchemy import String
        required_account = {'account_id', 'username', 'password_hash', 'full_name', 'email', 'phone_number',
                            'profile_id', 'status', 'auth_version', 'created_at'}
        if not required_account.issubset(columns) or not isinstance(columns['account_id']['type'], String):
            raise RuntimeError('The existing user_account table is not the twelve-story account schema. Back it up and review a migration; no account records were deleted.')
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
    upgrade_sprints_4_5()
    upgrade_report_activity()


def upgrade_sprints_4_5():
    """Add counts and category relationships while retaining project/category IDs."""
    dialect = db.engine.dialect.name
    with db.engine.begin() as connection:
        inspector = inspect(connection)
        columns = {column['name'] for column in inspector.get_columns('interior_design_project')}
        if 'view_count' not in columns:
            connection.execute(text('ALTER TABLE interior_design_project ADD COLUMN view_count INTEGER NOT NULL DEFAULT 0'))
        # Earlier stories stored category IDs before the category use cases existed.
        # Retain those IDs and their projects, giving managers editable category records.
        missing = connection.execute(text('SELECT DISTINCT p.category_id FROM interior_design_project p '
            'LEFT JOIN category c ON c.category_id = p.category_id WHERE c.category_id IS NULL')).scalars().all()
        for category_id in missing:
            name = f'Existing category {category_id}'
            while connection.execute(text('SELECT 1 FROM category WHERE LOWER(category_name) = LOWER(:name)'),
                                     {'name':name}).first():
                name += ' (imported)'
            connection.execute(text('INSERT INTO category (category_id, category_name, description) '
                'VALUES (:id, :name, :description)'), dict(id=category_id, name=name,
                    description='Category retained for existing projects.'))
        if dialect == 'postgresql':
            maximum = connection.execute(text('SELECT MAX(category_id) FROM category')).scalar()
            if maximum is not None:
                sequence = connection.execute(text("SELECT pg_get_serial_sequence('category', 'category_id')")).scalar()
                # The server returns a quoted, qualified sequence identifier.
                last_value = connection.execute(text('SELECT last_value FROM ' + sequence)).scalar()
                connection.execute(text("SELECT setval(pg_get_serial_sequence('category', 'category_id'), :maximum, true)"),
                                   {'maximum':max(maximum, last_value)})
            foreign_keys = inspector.get_foreign_keys('interior_design_project')
            if not any(fk['referred_table'] == 'category' and fk['constrained_columns'] == ['category_id'] for fk in foreign_keys):
                connection.execute(text('ALTER TABLE interior_design_project ADD CONSTRAINT fk_project_category '
                    'FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE RESTRICT'))
        elif dialect == 'sqlite':
            # SQLite cannot add a foreign key to an existing table with ALTER.
            # These triggers also cover upgraded SQLite installations without a table rebuild.
            for operation in ('INSERT', 'UPDATE OF category_id'):
                name = 'insert' if operation == 'INSERT' else 'update'
                connection.execute(text(f'CREATE TRIGGER IF NOT EXISTS project_category_{name} BEFORE {operation} '
                    'ON interior_design_project FOR EACH ROW WHEN NOT EXISTS '
                    '(SELECT 1 FROM category WHERE category_id = NEW.category_id) '
                    "BEGIN SELECT RAISE(ABORT, 'Category not found'); END"))
            connection.execute(text('CREATE TRIGGER IF NOT EXISTS category_in_use BEFORE DELETE ON category '
                'FOR EACH ROW WHEN EXISTS (SELECT 1 FROM interior_design_project WHERE category_id = OLD.category_id) '
                "BEGIN SELECT RAISE(ABORT, 'Category is used by projects'); END"))
        report_checks = {
            'ck_report_type': "report_type IN ('daily', 'weekly', 'monthly')",
            'ck_report_date_range': 'end_date >= start_date',
        }
        if dialect == 'postgresql':
            existing_checks = {check['name'] for check in inspector.get_check_constraints('report')}
            for name, condition in report_checks.items():
                if name not in existing_checks:
                    connection.execute(text(f'ALTER TABLE report ADD CONSTRAINT {name} CHECK ({condition})'))
        elif dialect == 'sqlite':
            for operation in ('INSERT', 'UPDATE'):
                connection.execute(text(f'CREATE TRIGGER IF NOT EXISTS report_valid_{operation.lower()} '
                    f'BEFORE {operation} ON report FOR EACH ROW WHEN '
                    "NEW.report_type NOT IN ('daily', 'weekly', 'monthly') OR NEW.end_date < NEW.start_date "
                    "BEGIN SELECT RAISE(ABORT, 'Invalid report type or date range'); END"))


def upgrade_report_activity():
    """Preserve category history for the report's new-IDP ranking."""
    with db.engine.begin() as connection:
        columns = {column['name'] for column in inspect(connection).get_columns('activity_event')}
        for name, sql_type in [('category_id', 'INTEGER'), ('category_name', 'VARCHAR(100)')]:
            if name not in columns:
                connection.execute(text(f'ALTER TABLE activity_event ADD COLUMN {name} {sql_type}'))
        # Older events have only a project ID. Recover the available category from
        # surviving projects without inventing history for already-deleted projects.
        connection.execute(text("""
            UPDATE activity_event AS event
            SET category_id = COALESCE(event.category_id, (
                    SELECT project.category_id FROM interior_design_project AS project
                    WHERE CAST(project.project_id AS VARCHAR) = event.target_id)),
                category_name = COALESCE(event.category_name, (
                    SELECT category.category_name FROM interior_design_project AS project
                    JOIN category ON category.category_id = project.category_id
                    WHERE CAST(project.project_id AS VARCHAR) = event.target_id))
            WHERE event.kind = 'project_new_created'
              AND (event.category_id IS NULL OR event.category_name IS NULL)
        """))
