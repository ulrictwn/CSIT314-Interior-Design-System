"""Shared sprint data and disposable databases; never use the app database."""
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# Set before importing app.py, which constructs a global app on import.
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SECRET_KEY'] = 'pytest-only-key-not-used-by-the-running-application'

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
        schema = 'sprint_test_' + uuid4().hex
        admin_engine = create_engine(url)
        with admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        options = {'connect_args': {'options': f'-csearch_path={schema}'}}
        uri = url
    else:
        uri = 'sqlite:///' + str(tmp_path / 'sprints.sqlite')
    application = None
    try:
        application = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': uri,
            'SQLALCHEMY_ENGINE_OPTIONS': options,
            'SESSION_COOKIE_SECURE': False,
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
    return dict(profileName='Test_Story_1_create',
                description='This profile is created for TC-1-TC-07.',
                status='Active', permissions=['profile.view', 'profile.search'])


@pytest.fixture
def seed_profile(app):
    def create(name='Customer', description='Customer role', status='Active', permissions=None):
        with app.app_context():
            profile = UserProfile(name=name, description=description, status=status,
                                  permissions=['profile.view'] if permissions is None else permissions)
            db.session.add(profile)
            db.session.commit()
            return profile.profile_id
    return create


@pytest.fixture
def profile_snapshot(app):
    def read(profile_id):
        with app.app_context():
            profile = db.session.get(UserProfile, profile_id)
            return dict(name=profile.name, description=profile.description,
                        status=profile.status, permissions=list(profile.permissions))
    return read


@pytest.fixture
def create_account(app, seed_profile):
    from entity.accounts.user_account import UserAccount

    def create(username='customer1', role='Customer', password=None):
        with app.app_context():
            profile = UserProfile.getProfile(role)
            profile_id = profile.profile_id if profile else seed_profile(role, permissions=[])
            account = UserAccount()
            assert account.createUserAccount(username, 'Name ' + username,
                username + '@example.com', '+65 6123 4567', profile_id, password=password)
            return account.account_id
    return create


@pytest.fixture
def customer_account(create_account):
    return create_account()


@pytest.fixture
def designer_account(create_account):
    return create_account('designer1', 'Interior Designer')


@pytest.fixture
def credentials():
    return dict(username='demo_user', password='Classroom-Password-123')


@pytest.fixture
def company_data():
    return dict(companyName='Demo Studio', companyContact='+65 6123 4567',
                companyAddress='10 Demo Road', companyEmail='studio@example.com',
                companyRegistrationNumber='DEMO-123')


@pytest.fixture
def company_profile(app, designer_account, company_data):
    from entity.company.company_profile import CompanyProfile

    with app.app_context():
        assert CompanyProfile().createCompanyProfile(designer_account, **company_data)
    return designer_account


@pytest.fixture
def category_data():
    return dict(categoryName='Japandi', description='Warm, natural interiors.')


@pytest.fixture
def category_id(app, category_data):
    from entity.categories.category import Category

    with app.app_context():
        category = Category(category_name=category_data['categoryName'],
                            description=category_data['description'])
        db.session.add(category)
        db.session.commit()
        return category.category_id


@pytest.fixture
def project_data(category_id):
    return dict(projectName='Seaside Home', categoryId=category_id,
                propertyType='Apartment', area='Bedok', renovationCost=80000.5,
                description='A bright renovation project.')


@pytest.fixture
def new_project(app, designer_account, project_data):
    from entity.projects.interior_design_project import InteriorDesignProject

    with app.app_context():
        project = InteriorDesignProject()
        assert project.createNewProject(designer_account, **project_data)
        return project.project_id


@pytest.fixture
def past_project(app, designer_account, project_data):
    from entity.projects.interior_design_project import InteriorDesignProject

    with app.app_context():
        project = InteriorDesignProject()
        assert project.createPastProject(designer_account,
            **dict(project_data, projectName='Courtyard Retreat'))
        return project.project_id


@pytest.fixture
def saved_project(app, customer_account, new_project):
    from entity.shortlist.shortlist import Shortlist

    with app.app_context():
        assert Shortlist().saveShortlist(customer_account, new_project)
    return new_project
