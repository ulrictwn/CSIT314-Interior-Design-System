import pytest
from infrastructure.database import db
from entity.user_profile import UserProfile

pytestmark = pytest.mark.story1


def test_TC01_create_form_has_required_fields_and_permission_checkboxes(client):
    response = client.get('/profiles/create')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for name in ('profileName', 'description', 'status', 'permissions', 'csrf_token'):
        assert f'name="{name}"' in html
    assert 'type="checkbox"' in html


def test_TC02_create_persists_trimmed_fields_and_selected_permissions(app, submit, profile_data):
    response = submit('/profiles/create', {**profile_data, 'profileName': '  Customer  ', 'description': '  Customer role  '})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/profiles')
    with app.app_context():
        profile = UserProfile.getProfile('Customer')
        assert (profile.name, profile.description, profile.status) == ('Customer', 'Customer role', 'Active')
        assert profile.permissions == profile_data['permissions']


def test_TC03_case_insensitive_duplicate_is_rejected_without_extra_row(app, seed, submit, profile_data):
    seed()
    response = submit('/profiles/create', {**profile_data, 'profileName': 'cUsToMeR'})
    assert response.status_code == 400
    assert 'already exists' in response.get_data(as_text=True)
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(UserProfile)) == 1


@pytest.mark.parametrize('field', ['profileName', 'description', 'status'])
def test_TC04_create_rejects_missing_required_field(app, submit, profile_data, field):
    data = {**profile_data, field: ''}
    assert submit('/profiles/create', data).status_code == 400
    with app.app_context():
        assert UserProfile.listUserProfiles() == []


@pytest.mark.parametrize('patch', [{'status': 'Unknown'}, {'permissions': ['profile.destroy']}], ids=['unknown-status', 'unknown-permission'])
def test_TC05_create_rejects_unrecognized_choices(app, submit, profile_data, patch):
    assert submit('/profiles/create', {**profile_data, **patch}).status_code == 400
    with app.app_context():
        assert UserProfile.listUserProfiles() == []


@pytest.mark.parametrize('field,length', [('profileName', 101), ('description', 10001)])
def test_TC06_create_rejects_overlong_text(submit, profile_data, field, length):
    assert submit('/profiles/create', {**profile_data, field: 'x' * length}).status_code == 400


def test_TC07_create_allows_empty_permissions(app, submit, profile_data):
    assert submit('/profiles/create', {**profile_data, 'permissions': []}).status_code == 302
    with app.app_context():
        assert UserProfile.getProfile('Customer').permissions == []