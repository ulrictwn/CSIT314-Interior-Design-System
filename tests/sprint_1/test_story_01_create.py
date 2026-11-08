"""Story 1: TC01–TC07 from the Word document's Checks list."""
import pytest
from entity.profile.user_profile import UserProfile

pytestmark = [pytest.mark.sprint1, pytest.mark.story1]


def test_TC01_create_form_renders_and_incomplete_submission_is_not_saved(app, admin_client, form_controls):
    response = admin_client.get('/profiles/create')
    assert response.status_code == 200
    assert '<form method="post">' in response.text
    controls = form_controls(response.text)
    for name in ('profileName', 'description', 'status'):
        field = next(item for item in controls if item.get('name') == name)
        assert 'required' in field
    permissions = [item for item in controls if item.get('name') == 'permissions']
    assert permissions and all(item.get('type') == 'checkbox' for item in permissions)
    assert admin_client.post('/profiles/create', data={}).status_code == 400
    with app.app_context():
        assert [profile.name for profile in UserProfile.listUserProfiles()] == ['User Admin']


def test_TC02_valid_submission_saves_fields_and_permissions(app, admin_client, profile_data):
    response = admin_client.post('/profiles/create', data=profile_data, follow_redirects=True)
    assert response.status_code == 200
    assert 'User profile created successfully.' in response.text
    assert profile_data['profileName'] in response.text
    with app.app_context():
        profile = UserProfile.getProfile(profile_data['profileName'])
        assert profile.description == profile_data['description']
        assert profile.status == 'Active'
        assert profile.permissions == profile_data['permissions']


def test_TC03_duplicate_names_are_rejected_regardless_of_capitalization(app, admin_client, seed_profile, profile_data):
    seed_profile(profile_data['profileName'])
    response = admin_client.post('/profiles/create', data=dict(profile_data, profileName=profile_data['profileName'].upper()))
    assert response.status_code == 400
    assert 'already exists' in response.text
    with app.app_context():
        assert len(UserProfile.listUserProfiles()) == 2


def test_TC04_each_missing_required_field_is_rejected(app, admin_client, profile_data):
    for field in ('profileName', 'description', 'status'):
        with app.app_context():
            entity = UserProfile()
            assert entity.createUserProfile(**{**profile_data, field: ''}) is False
            assert field in entity.field_errors
        response = admin_client.post('/profiles/create', data={**profile_data, field: ''})
        assert response.status_code == 400, field
        with app.app_context():
            assert [profile.name for profile in UserProfile.listUserProfiles()] == ['User Admin']


def test_TC05_unknown_status_is_rejected(app, admin_client, profile_data):
    assert admin_client.post('/profiles/create', data=dict(profile_data, status='Unknown')).status_code == 400
    with app.app_context():
        assert [profile.name for profile in UserProfile.listUserProfiles()] == ['User Admin']


def test_TC06_overlong_names_and_descriptions_are_rejected(app, admin_client, profile_data):
    for field, length in (('profileName', 101), ('description', 10001)):
        response = admin_client.post('/profiles/create', data={**profile_data, field: 'x' * length})
        assert response.status_code == 400, field
        with app.app_context():
            assert [profile.name for profile in UserProfile.listUserProfiles()] == ['User Admin']


def test_TC07_profile_can_be_created_without_permissions(app, admin_client, profile_data):
    assert admin_client.post('/profiles/create', data=dict(profile_data, permissions=[])).status_code == 302
    with app.app_context():
        assert UserProfile.getProfile(profile_data['profileName']).permissions == []
