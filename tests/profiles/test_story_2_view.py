import pytest
from flask import g
from unittest.mock import Mock
from boundary.profile.view_user_profile_page import ViewUserProfilePage
from control.profile.view_user_profile_controller import ViewUserProfileController
from infrastructure.database import db
from infrastructure.errors import AccessError
from entity.profile.user_profile import UserProfile

pytestmark = pytest.mark.story2


def test_TC08_directory_displays_profiles_and_statuses(client, seed):
    seed('Customer')
    seed('Obsolete role', status='Suspended')
    page = client.get('/profiles')
    assert page.status_code == 200
    for text in ('Customer', 'Obsolete role', 'Active', 'Suspended'):
        assert text in page.get_data(as_text=True)


def test_TC09_detail_displays_fields_and_escapes_html(client, seed):
    profile_id = seed('Customer', description='<script>alert(1)</script>', permissions=['profile.search'])
    page = client.get(f'/profiles/{profile_id}')
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert 'Search user profiles' in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '<script>alert(1)</script>' not in html


def test_TC10_missing_profile_returns_404(client):
    assert client.get('/profiles/999999').status_code == 404


def test_TC11_profiles_have_predictable_name_order(app, seed):
    seed('Zebra'); seed('Alpha')
    with app.app_context():
        assert [profile.name for profile in UserProfile.listUserProfiles()] == ['Alpha', 'Zebra']


class Actor:
    def __init__(self, permissions):
        self.permissions = set(permissions)

    def has_permission(self, permission):
        return permission in self.permissions


def test_sidebar_uses_search_for_profiles_and_accounts(admin_client):
    response = admin_client.get('/profiles/search')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    sidebar = html.partition('<nav id="primary-navigation"')[2].partition('</nav>')[0]
    assert sidebar
    assert 'View User Profiles' not in sidebar
    assert 'Search User Profiles' in sidebar
    assert 'View User Accounts' not in sidebar
    assert 'Search User Accounts' in sidebar


def test_search_view_button_opens_profile_details_and_links_back(client, seed):
    profile_id = seed('Review role', description='Role details', permissions=['profile.search'])
    response = client.get('/profiles/search', query_string={'q': 'Review role'})
    assert response.status_code == 200
    assert f'href="/profiles/{profile_id}"' in response.get_data(as_text=True)
    response = client.get(f'/profiles/{profile_id}')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for text in ('Review role', 'Role details', 'Active', 'Search user profiles'):
        assert text in html
    assert 'href="/profiles/search">Back to search</a>' in html


def test_view_only_actor_can_read_details_without_search_access(app, client, seed):
    profile_id = seed()
    app.config['PROFILE_ACTOR_LOADER'] = lambda: Actor(['profile.view'])
    response = client.get(f'/profiles/{profile_id}')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Back to profiles' in html
    assert 'Back to search' not in html
    assert client.get('/profiles/search').status_code == 403


def test_search_permission_does_not_grant_profile_view(app, client, seed):
    profile_id = seed()
    app.config['PROFILE_ACTOR_LOADER'] = lambda: Actor(['profile.search'])
    response = client.get('/profiles/search')
    assert response.status_code == 200
    assert f'href="/profiles/{profile_id}"' not in response.get_data(as_text=True)
    assert client.get(f'/profiles/{profile_id}').status_code == 403
    with pytest.raises(AccessError):
        ViewUserProfileController(Actor(['profile.search'])).getUserProfile(profile_id)


@pytest.mark.parametrize('profile_id', [None, True, False, 0, -1, '1', 1.5, 2_147_483_648])
def test_entity_rejects_invalid_profile_id_without_querying(monkeypatch, profile_id):
    lookup = Mock(side_effect=AssertionError('Invalid profile ID reached the database'))
    monkeypatch.setattr(db.session, 'get', lookup)
    assert UserProfile.getUserProfile(profile_id) is None
    lookup.assert_not_called()


@pytest.mark.parametrize('exists', [True, False])
def test_on_view_returns_void_and_prepares_the_http_response(app, seed, exists):
    profile_id = seed('Review role', description='Role details')
    requested_id = profile_id if exists else profile_id + 1
    with app.test_request_context(f'/profiles/{requested_id}'):
        g.profile_actor = Actor(['profile.view'])
        page = ViewUserProfilePage()
        assert page.onView(requested_id) is None
        if exists:
            assert 'Role details' in page.rendered_page
        else:
            html, status = page.rendered_page
            assert status == 404
            assert 'User profile not found.' in html


def test_entity_lookup_returns_the_requested_profile_and_none_if_missing(app, seed):
    profile_id = seed('Review role')
    with app.app_context():
        assert UserProfile.getUserProfile(profile_id).name == 'Review role'
        assert UserProfile.getUserProfile(profile_id + 1) is None
