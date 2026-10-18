import pytest
from entity.user_profile import UserProfile

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
