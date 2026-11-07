"""Boundary input validation and entity duplicate/persistence contracts."""
import pytest
from unittest.mock import Mock

from control.profile.create_user_profile_controller import CreateUserProfileController
from boundary.profile.create_user_profile_page import CreateUserProfilePage
from entity.profile.user_profile import UserProfile
from infrastructure.database import db


pytestmark = pytest.mark.story1


@pytest.mark.parametrize('patch, field', [
    ({'profileName': ''}, 'profileName'),
    ({'profileName': None}, 'profileName'),
    ({'profileName': 'x' * 101}, 'profileName'),
    ({'description': '   '}, 'description'),
    ({'description': 'x' * 10001}, 'description'),
    ({'status': None}, 'status'),
    ({'status': True}, 'status'),
    ({'status': 1}, 'status'),
    ({'permissions': ['profile.destroy']}, 'permissions'),
    ({'permissions': 'profile.view'}, 'permissions'),
    ({'permissions': [None]}, 'permissions'),
])
def test_boundary_rejects_invalid_input_before_controller_access(app, monkeypatch, profile_data, patch, field):
    create = Mock(side_effect=AssertionError('Invalid data reached the controller'))
    monkeypatch.setattr(CreateUserProfileController, 'createUserProfile', create)
    with app.test_request_context('/profiles/create', method='POST'):
        page = CreateUserProfilePage()
        assert page.onCreate(**{**profile_data, 'status': 'Active', **patch}) is None
        assert field in page.field_errors
        assert page.rendered_page[1] == 400
    create.assert_not_called()


@pytest.mark.parametrize('status, stored_status', [(True, 'Active'), (False, 'Suspended')])
def test_boundary_trims_fields_and_permissions_before_entity_saves(app, submit, status, stored_status):
    response = submit('/profiles/create', dict(profileName='  Customer  ', description='  Customer role  ',
        status=stored_status, permissions=['profile.view', 'profile.view', 'profile.search']))
    assert response.status_code == 302
    with app.app_context():
        saved = UserProfile.getProfile('customer')
        assert (saved.name, saved.description, saved.status) == ('Customer', 'Customer role', stored_status)
        assert saved.permissions == ['profile.view', 'profile.search']


@pytest.mark.parametrize('concurrent_insert', [False, True])
def test_entity_rejects_duplicates_and_keeps_session_usable(app, seed, monkeypatch, concurrent_insert):
    seed('Customer')
    with app.app_context():
        if concurrent_insert:
            # Simulate a competing insert after the preliminary name check.
            monkeypatch.setattr(UserProfile, 'userProfileExists', lambda *args: False)
        profile = UserProfile()
        assert profile.createUserProfile('cUsToMeR', 'Duplicate', 'Active', []) is False
        assert 'already exists' in profile.error_message
        assert len(UserProfile.listUserProfiles()) == 1
        assert UserProfile().createUserProfile('Designer', 'Another role', 'Suspended', []) is True
        assert len(UserProfile.listUserProfiles()) == 2


def test_controller_relays_boolean_result_and_entity_errors(app, profile_data):

    with app.app_context():
        controller = CreateUserProfileController()
        assert controller.createUserProfile(**{**profile_data, 'status': 'Active'}) is True
        assert controller.userProfileExists('customer') is True
        assert controller.createUserProfile(**{**profile_data, 'status': 'Active'}) is False
        assert 'already exists' in controller.error_message
        assert 'profileName' in controller.field_errors


def test_web_invalid_input_stops_at_boundary_and_redisplays_values(app, submit, monkeypatch, profile_data):
    received = []
    create = UserProfile.createUserProfile

    def observe(self, profileName, description, status, permissions):
        received.append((profileName, status, permissions))
        return create(self, profileName, description, status, permissions)

    monkeypatch.setattr(UserProfile, 'createUserProfile', observe)
    response = submit('/profiles/create', {
        **profile_data, 'profileName': '', 'status': 'Unknown', 'permissions': ['profile.destroy']})
    assert response.status_code == 400
    assert received == []
    html = response.get_data(as_text=True)
    assert 'Profile name is required.' in html
    assert 'Choose Active or Suspended.' in html
    assert 'Choose permissions from the supported list.' in html
    assert profile_data['description'] in html
    with app.app_context():
        assert UserProfile.listUserProfiles() == []


def test_web_suspended_selection_creates_suspended_profile(app, submit, profile_data):
    response = submit('/profiles/create', {**profile_data, 'status': 'Suspended'})
    assert response.status_code == 302
    with app.app_context():
        assert UserProfile.getProfile('Customer').status == 'Suspended'
