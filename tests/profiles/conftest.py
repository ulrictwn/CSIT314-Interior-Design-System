"""Disposable databases only. Never consume the application's DATABASE_URL/.env."""
import os
import re
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# Set before importing app.py, which constructs a global app on import.
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'pytest-only-key-not-used-by-the-running-application'
os.environ['COOKIE_SECURE'] = 'false'
os.environ['PROFILE_DEVELOPMENT_PREVIEW'] = 'false'

from app import create_app
from infrastructure.database import db
from entity.profile.user_profile import UserProfile


@pytest.fixture
def app(tmp_path):
    target = os.getenv('TEST_DATABASE_URL')
    admin_engine = None
    schema = None
    options = {}
    if target:
        url = make_url(target)
        if url.drivername != 'postgresql+psycopg' or url.database != 'nestora_test':
            raise RuntimeError('TEST_DATABASE_URL must use postgresql+psycopg and the dedicated nestora_test database. Your app database is never accepted.')
        schema = 'profile_test_' + uuid4().hex
        admin_engine = create_engine(url)
        with admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        options = {'connect_args': {'options': f'-csearch_path={schema}'}}
        uri = url
    else:
        uri = 'sqlite:///' + str(tmp_path / 'profiles.sqlite')
    application = None
    try:
        application = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': uri,
            'SQLALCHEMY_ENGINE_OPTIONS': options,
            'PROFILE_DEVELOPMENT_PREVIEW': True,
            'PROFILE_ACTOR_LOADER': None,
            'SESSION_COOKIE_SECURE': False,
            'WTF_CSRF_ENABLED': True,
        })
        with application.app_context():
            db.create_all()
        yield application
    finally:
        if application is not None:
            with application.app_context():
                db.session.remove()
                db.engine.dispose()
        if admin_engine is not None:
            try:
                with admin_engine.begin() as connection:
                    connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
            finally:
                admin_engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def profile_data():
    return dict(profileName='Customer', description='Customers can explore design ideas.',
                status='Active', permissions=['profile.view', 'profile.search'])


@pytest.fixture
def submit(client):
    def submit_form(url, data):
        page = client.get(url)
        assert page.status_code == 200, (url, page.status_code)
        match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.get_data(as_text=True))
        assert match, f'CSRF field missing from {url}'
        return client.post(url, data={'csrf_token': match.group(1), **data})
    return submit_form


@pytest.fixture
def seed(app):
    def create(name='Customer', description='Customer role', status='Active', permissions=None):
        with app.app_context():
            record = UserProfile(name=name, description=description, status=status,
                                 permissions=['profile.view'] if permissions is None else permissions)
            db.session.add(record)
            db.session.commit()
            return record.profile_id
    return create


@pytest.fixture
def snapshot(app):
    def read(profile_id):
        with app.app_context():
            record = db.session.get(UserProfile, profile_id)
            return None if record is None else dict(profile_id=record.profile_id, name=record.name,
                description=record.description, status=record.status, permissions=list(record.permissions))
    return read


@pytest.fixture
def account_assignment(app):
    def assign(profile_id, table_name='user_account', status='Active'):
        assert table_name in ('user_account', 'user_accounts')
        with app.app_context():
            if table_name == 'user_account':
                from entity.accounts.user_account import UserAccount
                username = 'fixture_' + uuid4().hex[:12]
                assert UserAccount().createUserAccount(username, 'Fixture Account',
                    username+'@example.com', '+65 6123 4567', profile_id)
                account = UserAccount.getByUsername(username)
                account.status = status
            else:
                db.session.execute(text(f'CREATE TABLE {table_name} (account_id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL, status VARCHAR(20))'))
                db.session.execute(text(f'INSERT INTO {table_name} (account_id, profile_id, status) VALUES (1, :id, :status)'),
                                   {'id': profile_id, 'status': status})
            db.session.commit()
    return assign


ADMIN_PASSWORD = 'Review-Administrator-Password-123'

def login_client(client, username, password=ADMIN_PASSWORD):
    page = client.get('/login')
    assert page.status_code == 200
    token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.get_data(as_text=True)).group(1)
    return client.post('/login', data={'username':username, 'password':password, 'csrf_token':token})

@pytest.fixture
def admin_client(app, client):
    app.config.update(PROFILE_DEVELOPMENT_PREVIEW=False, PROFILE_ACTOR_LOADER=None)
    result = app.test_cli_runner().invoke(args=['bootstrap-admin', '--username','admin', '--email','admin@example.com',
        '--full-name','Review Administrator', '--phone-number','+65 6123 4567'], env={'NESTORA_ADMIN_PASSWORD':ADMIN_PASSWORD})
    assert result.exit_code == 0, result.output
    assert login_client(client, 'admin').status_code == 302
    return client

@pytest.fixture
def create_account(app, admin_client, submit):
    def create(username='customer1', role='Customer'):
        with app.app_context():
            profile_id = UserProfile.getProfile(role).profile_id
        data = dict(username=username,
            full_name='Name '+username, email=username+'@example.com', phone_number='+65 6123 4567', profile_id=profile_id)
        response = submit('/accounts/create', data)
        assert response.status_code == 302, response.get_data(as_text=True)
        with app.app_context():
            from entity.accounts.user_account import UserAccount
            return UserAccount.getByUsername(username).account_id
    return create


@pytest.fixture
def set_account_password(app):
    def configure(username, password=ADMIN_PASSWORD):
        result = app.test_cli_runner().invoke(args=['reset-password', '--username', username],
            input=password + '\n' + password + '\n')
        assert result.exit_code == 0, result.output
    return configure


@pytest.fixture
def sign_in(app):
    def sign_in(username, password=ADMIN_PASSWORD):
        client = app.test_client()
        return client, login_client(client, username, password)
    return sign_in
