"""Story 2: TC08–TC11 from the Word document."""
import pytest

pytestmark = [pytest.mark.sprint1, pytest.mark.story2]


def test_TC08_list_displays_active_and_suspended_profiles_with_statuses(admin_client, seed_profile):
    seed_profile('Active Customer', status='Active')
    seed_profile('Retired Designer', status='Suspended')
    response = admin_client.get('/profiles')
    assert response.status_code == 200
    for text in ('Active Customer', 'Retired Designer', 'Active', 'Suspended'):
        assert text in response.text


def test_TC09_profile_details_are_correct(admin_client, seed_profile):
    profile_id = seed_profile('test_story_2_view', description='This profile is being viewed for TC8 to TC11.',
                              permissions=['profile.search'])
    response = admin_client.get(f'/profiles/{profile_id}')
    assert response.status_code == 200
    for text in ('test_story_2_view', 'This profile is being viewed for TC8 to TC11.',
                 'Active', 'Search user profiles'):
        assert text in response.text


def test_TC10_viewing_nonexistent_profile_returns_error(admin_client):
    assert admin_client.get('/profiles/999999').status_code == 404


def test_TC11_profiles_are_listed_in_alphabetical_order(admin_client, seed_profile):
    seed_profile('Zebra Role')
    seed_profile('Alpha Role')
    response = admin_client.get('/profiles')
    assert response.status_code == 200
    assert response.text.index('Alpha Role') < response.text.index('Zebra Role')
