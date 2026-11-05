import pytest
from sqlalchemy import Table, MetaData, Column, Integer, String, Text, JSON, inspect, text
from sqlalchemy.dialects.postgresql import ARRAY
from entity.profile.user_profile import UserProfile
from infrastructure.database import db
from infrastructure.migrations import upgrade_database
from infrastructure.errors import DomainError


@pytest.mark.database
@pytest.mark.parametrize('legacy_name', ['user_profile', 'user_profiles'])
def test_TC39_legacy_upgrade_preserves_profile_and_adds_status(app, legacy_name):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        legacy = Table(legacy_name, MetaData(), Column('profile_id', Integer, primary_key=True),
            Column('name', String(100), nullable=False), Column('description', Text, nullable=False),
            Column('permissions', JSON().with_variant(ARRAY(Text), 'postgresql'), nullable=False))
        legacy.create(db.engine)
        with db.engine.begin() as connection:
            connection.execute(legacy.insert().values(profile_id=1, name='Existing role',
                description='Retained description', permissions=['profile.view']))
        upgrade_database()
        upgrade_database()  # Re-running setup must not erase or duplicate records.
        profile = db.session.get(UserProfile, 1)
        assert (profile.name, profile.description, profile.status, profile.permissions) == (
            'Existing role', 'Retained description', 'Active', ['profile.view'])
        assert 'user_profile' in inspect(db.engine).get_table_names()


@pytest.mark.database
def test_TC40_upgrade_stops_for_duplicate_names_without_deleting_rows(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        with db.engine.begin() as connection:
            connection.execute(text('CREATE TABLE user_profile (profile_id INTEGER PRIMARY KEY, name VARCHAR(100), description TEXT, permissions TEXT, status VARCHAR(20))'))
            connection.execute(text("INSERT INTO user_profile VALUES (1, 'Role', 'First', '[]', 'Active'), (2, 'role', 'Second', '[]', 'Active')"))
        with pytest.raises(RuntimeError, match='capitalisation'):
            upgrade_database()
        with db.engine.connect() as connection:
            assert connection.scalar(text('SELECT COUNT(*) FROM user_profile')) == 2


@pytest.mark.database
def test_TC41_upgrade_rejects_unknown_schema_without_deleting_table(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        with db.engine.begin() as connection:
            connection.execute(text('CREATE TABLE user_profile (unfamiliar_id INTEGER PRIMARY KEY)'))
        with pytest.raises(RuntimeError, match='unfamiliar structure'):
            upgrade_database()
        assert 'user_profile' in inspect(db.engine).get_table_names()


@pytest.mark.database
def test_TC42_ambiguous_existing_account_schema_blocks_suspension(app, seed, submit, snapshot):
    profile_id = seed()
    with app.app_context():
        db.session.execute(text('CREATE TABLE user_accounts (account_id INTEGER PRIMARY KEY, custom_role INTEGER)'))
        db.session.commit()
    response = submit(f'/profiles/{profile_id}/suspend', {})
    assert response.status_code == 400
    assert 'assignment mapping' in response.get_data(as_text=True)
    assert snapshot(profile_id)['status'] == 'Active'


@pytest.mark.database
def test_TC43_permission_storage_type_matches_database_and_round_trips(app, seed, snapshot):
    profile_id = seed(permissions=['profile.view', 'profile.search'])
    with app.app_context():
        permissions = next(c for c in inspect(db.engine).get_columns('user_profile') if c['name'] == 'permissions')
        if db.engine.dialect.name == 'postgresql':
            assert isinstance(permissions['type'], ARRAY)
        else:
            assert isinstance(permissions['type'], JSON)
    assert snapshot(profile_id)['permissions'] == ['profile.view', 'profile.search']


@pytest.mark.story5
def test_TC44_unsupported_directory_operation_is_rejected(client):
    assert client.get('/profiles?mode=destroy').status_code == 400
