"""Profile story contracts and validation independent of HTML form classes."""
from unittest.mock import Mock

import pytest
from flask import g

from boundary.profile.update_user_profile_page import UpdateUserProfilePage
from boundary.profile.suspend_user_profile_page import SuspendUserProfilePage
from boundary.profile.search_user_profile_page import SearchUserProfilePage
from control.profile.update_user_profile_controller import UpdateUserProfileController
from control.profile.suspend_user_profile_controller import SuspendUserProfileController
from control.profile.search_user_profile_controller import SearchUserProfileController
from entity.profile.user_profile import UserProfile
from infrastructure.database import db
from infrastructure.errors import DomainError


@pytest.mark.story3
@pytest.mark.parametrize('patch', [
    {'profileId': 0}, {'profileId': True}, {'profileId': '1'},
    {'profileName': ''}, {'profileName': 'x' * 101},
    {'description': None}, {'description': 'x' * 10001},
    {'permissions': ['profile.destroy']}, {'permissions': 'profile.view'},
    {'permissions': [None]},
])
def test_update_boundary_rejects_invalid_data_before_controller_access(app, monkeypatch, profile_data, patch):
    update = Mock(side_effect=AssertionError('Invalid update reached the controller'))
    monkeypatch.setattr(UpdateUserProfileController, 'updateUserProfile', update)
    with app.test_request_context('/profiles/1/update', method='POST'):
        page = UpdateUserProfilePage()
        data = {**profile_data, 'profileId': 1, **patch}
        data.pop('status')
        assert page.onUpdate(**data) is None
        assert page.error_message
        assert page.rendered_page[1] in (400, 404)
    update.assert_not_called()


@pytest.mark.story3
def test_update_boundary_normalizes_diagram_arguments_and_preserves_status(app, seed, snapshot):
    profile_id = seed('Customer', status='Suspended')
    with app.test_request_context(f'/profiles/{profile_id}/update'):
        page = UpdateUserProfilePage()
        assert page.onUpdate(profile_id, '  Customer  ', '  Changed details  ', ['profile.view', 'profile.view']) is None
        assert page.rendered_page.status_code == 302
    assert snapshot(profile_id) == dict(profile_id=profile_id, name='Customer', description='Changed details',
                                      status='Suspended', permissions=['profile.view'])


@pytest.mark.story3
@pytest.mark.parametrize('initial, new_status, expected', [('Active', False, 'Suspended'), ('Suspended', True, 'Active')])
def test_update_uses_diagram_arguments_and_preserves_status(app, seed, snapshot, initial, new_status, expected):
    profile_id = seed(status=initial)
    with app.test_request_context(f'/profiles/{profile_id}/update', method='POST', data={'status': expected}):
        page = UpdateUserProfilePage()
        assert page.onUpdate(profile_id, 'Customer', 'Details', []) is None
        assert page.rendered_page.status_code == 302
    assert snapshot(profile_id)['status'] == initial


@pytest.mark.story3
@pytest.mark.parametrize('concurrent_insert', [False, True])
def test_update_duplicate_rolls_back_and_allows_a_followup_update(app, seed, snapshot, monkeypatch, concurrent_insert):
    profile_id = seed('Customer')
    seed('Designer')
    before = snapshot(profile_id)
    with app.app_context():
        if concurrent_insert:
            monkeypatch.setattr(UserProfile, 'userProfileExists', lambda *args: False)
        operation = UserProfile()
        assert operation.updateUserProfile(profile_id, 'designer', 'Rejected edit', []) is False
        assert 'already exists' in operation.error_message
        assert operation.field_errors['profileName']
        assert snapshot(profile_id) == before
        assert UserProfile().updateUserProfile(profile_id, 'Updated role', 'Saved edit', []) is True
    assert snapshot(profile_id)['name'] == 'Updated role'


@pytest.mark.story3
@pytest.mark.parametrize('status', ['', 'Unknown'])
def test_extra_status_input_is_ignored_by_diagram_update(app, seed, submit, snapshot, profile_data, monkeypatch, status):
    profile_id = seed()
    before = snapshot(profile_id)
    response = submit(f'/profiles/{profile_id}/update', {**profile_data, 'status': status})
    assert response.status_code == 302
    assert snapshot(profile_id)['status'] == before['status']


@pytest.mark.story4
@pytest.mark.parametrize('profile_id', [None, True, 0, -1])
def test_suspend_boundary_validates_id_before_controller_access(app, monkeypatch, profile_id):
    suspend = Mock(side_effect=AssertionError('Invalid suspension reached the controller'))
    monkeypatch.setattr(SuspendUserProfileController, 'suspendUserProfile', suspend)
    with app.test_request_context('/profiles/invalid/suspend', method='POST'):
        page = SuspendUserProfilePage()
        assert page.onSuspend(profile_id) is None
        assert page.error_reason == 'not_found'
        assert page.rendered_page[1] == 404
    suspend.assert_not_called()


@pytest.mark.story4
def test_suspend_entity_rejects_assignment_to_a_suspended_account(app, seed, account_assignment, snapshot):
    profile_id = seed()
    account_assignment(profile_id, status='Suspended')
    before = snapshot(profile_id)
    with app.app_context():
        operation = UserProfile()
        assert operation.suspendUserProfile(profile_id) is False
        assert operation.error_message == 'This profile is in use.'
    assert snapshot(profile_id) == before


@pytest.mark.story4
def test_suspend_entity_returns_boolean_and_persists_status(app, seed, snapshot):
    profile_id = seed()
    with app.app_context():
        assert UserProfile().suspendUserProfile(profile_id) is True
    assert snapshot(profile_id)['status'] == 'Suspended'


@pytest.mark.story5
@pytest.mark.parametrize('keyword', [None, '', '   ', 'x' * 201])
def test_search_boundary_validates_before_querying(app, monkeypatch, keyword):
    lookup = Mock(side_effect=AssertionError('Invalid search reached the controller'))
    monkeypatch.setattr(SearchUserProfileController, 'searchUserProfiles', lookup)
    monkeypatch.setattr(SearchUserProfileController, 'listUserProfiles', lambda self: [])
    with app.test_request_context('/profiles/search'):
        page = SearchUserProfilePage()
        assert page.onSearch(keyword) is None
        assert 'Search text' in page.rendered_page
    lookup.assert_not_called()


@pytest.mark.story5
@pytest.mark.parametrize('keyword, name', [('%', 'Literal%role'), ('_', 'Literal_role')])
def test_search_returns_a_list_and_treats_wildcards_literally(app, seed, keyword, name):
    seed(name)
    seed('Ordinary role')
    with app.app_context():
        profiles = SearchUserProfileController().searchUserProfiles(keyword)
        assert isinstance(profiles, list)
        assert [profile.name for profile in profiles] == [name]


@pytest.mark.parametrize('action', ['update', 'suspend'])
@pytest.mark.parametrize('exists', [True, False])
def test_mutation_boundary_events_return_void_and_prepare_responses(app, seed, action, exists):
    profile_id = seed('Review role')
    requested_id = profile_id if exists else profile_id + 1
    with app.test_request_context(f'/profiles/{requested_id}/{action}', method='POST'):
        if action == 'update':
            page = UpdateUserProfilePage()
            assert page.onUpdate(requested_id, 'Edited role', 'Details', []) is None
        else:
            page = SuspendUserProfilePage()
            assert page.onSuspend(requested_id) is None
        if exists:
            assert page.rendered_page.status_code == 302
        else:
            html, status = page.rendered_page
            assert status == 404
            assert 'User profile not found.' in html


@pytest.mark.story5
@pytest.mark.parametrize('keyword', ['Review role', '   '])
def test_search_boundary_event_returns_void_and_displays_results(app, seed, keyword):
    seed('Review role')
    with app.test_request_context('/profiles/search'):
        page = SearchUserProfilePage()
        assert page.onSearch(keyword) is None
        assert 'Review role' in page.rendered_page
