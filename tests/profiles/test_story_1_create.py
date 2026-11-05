import pytest
from html.parser import HTMLParser
from unittest.mock import Mock
from infrastructure.database import db
from entity.profile.user_profile import UserProfile

pytestmark = pytest.mark.story1


class FormControls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.controls = []

    def handle_starttag(self, tag, attrs):
        if tag in ('input', 'textarea', 'select'):
            self.controls.append(dict(attrs))


@pytest.mark.parametrize('check_id', ['TC01.1', 'TC01.2', 'TC01.3', 'TC01.4'], ids=str)
def test_TC01_create_form_checks(app, client, submit, profile_data, monkeypatch, check_id):
    # Every parameter is collected as a separate test with a fresh database.
    if check_id == 'TC01.1':
        response = client.get('/profiles/create')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert '<h1>Create User Profiles</h1>' in html
        assert '<form method="post">' in html

    elif check_id == 'TC01.2':
        parser = FormControls()
        parser.feed(client.get('/profiles/create').get_data(as_text=True))
        for name in ('profileName', 'description', 'status'):
            controls = [item for item in parser.controls if item.get('name') == name]
            assert len(controls) == 1, f'{name} must appear once'
            assert 'required' in controls[0], f'{name} must be marked required'

    elif check_id == 'TC01.3':
        response = client.get('/profiles/create')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert '<details class="permissions-dropdown"' in html
        parser = FormControls()
        parser.feed(html)
        choices = [item for item in parser.controls if item.get('name') == 'permissions']
        assert choices and all(item.get('type') == 'checkbox' for item in choices)
        assert any(item.get('value') == 'profile.view' for item in choices)
        # Rendering the dropdown must not create a record. Valid POST persistence
        # is covered by TC02; these are not preview-only/ignored permissions.
        with app.app_context():
            assert UserProfile.listUserProfiles() == []

    else:  # TC01.4: validate before querying or writing the database.
        forbidden_calls = {}
        for operation in ('execute', 'add', 'flush', 'commit'):
            guard = Mock(side_effect=AssertionError(f'Invalid form reached db.session.{operation}'))
            monkeypatch.setattr(db.session, operation, guard)
            forbidden_calls[operation] = guard
        for missing_field in ('profileName', 'description', 'status'):
            response = submit('/profiles/create', {**profile_data, missing_field: ''})
            assert response.status_code == 400, missing_field
            assert 'Please correct the errors below.' in response.get_data(as_text=True)
        for guard in forbidden_calls.values():
            guard.assert_not_called()


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



def test_create_error_preserves_escaped_values_status_and_permissions(seed, submit, profile_data):
    from markupsafe import escape

    class ControlsAndOptions(FormControls):
        selected_status = None

        def handle_starttag(self, tag, attrs):
            super().handle_starttag(tag, attrs)
            attributes = dict(attrs)
            if tag == 'option' and 'selected' in attributes:
                self.selected_status = attributes['value']

    name = 'Customer "<role>" & other'
    description = 'Keep </textarea><script>alert("test")</script> as text.'
    seed(name)
    values = {**profile_data, 'profileName': name, 'description': description, 'status': 'Suspended'}
    response = submit('/profiles/create', values)
    assert response.status_code == 400
    html = response.get_data(as_text=True)
    controls = ControlsAndOptions()
    controls.feed(html)
    name_control = next(item for item in controls.controls if item.get('name') == 'profileName')
    assert name_control['value'] == name
    assert name_control['aria-invalid'] == 'true'
    assert controls.selected_status == 'Suspended'
    assert {item['value'] for item in controls.controls
            if item.get('name') == 'permissions' and 'checked' in item} == set(values['permissions'])
    assert str(escape(description)) in html
    assert '<script>alert(' not in html
    assert 'already exists' in html


def test_create_error_form_can_be_corrected_and_resubmitted(app, client, submit, profile_data):
    response = submit('/profiles/create', {**profile_data, 'description': ''})
    assert response.status_code == 400
    controls = FormControls()
    controls.feed(response.get_data(as_text=True))
    response = client.post('/profiles/create', data=profile_data)
    assert response.status_code == 302
    with app.app_context():
        assert UserProfile.getProfile(profile_data['profileName']).description == profile_data['description']
