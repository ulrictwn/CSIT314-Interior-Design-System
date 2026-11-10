"""Story 5: TC19–TC22 from the Word document."""
import pytest
from entity.profile.user_profile import UserProfile
from infrastructure.errors import DomainError

pytestmark = [pytest.mark.sprint1, pytest.mark.story5]


def test_TC19_search_by_name_is_case_insensitive(admin_client, seed_profile):
    seed_profile('test_story_5_search')
    response = admin_client.get('/profiles/search', query_string={'q': 'TEST_STORY_5_SEARCH'})
    assert response.status_code == 200
    assert 'test_story_5_search' in response.text


def test_TC20_search_returns_existing_profile(admin_client, seed_profile):
    seed_profile('test_story_5_search', description='Scandinavian interiors')
    response = admin_client.get('/profiles/search', query_string={'q': 'Scandinavian'})
    assert response.status_code == 200
    assert 'test_story_5_search' in response.text


def test_TC21_unmatched_search_displays_no_profiles_found(admin_client, seed_profile):
    seed_profile('test_story_5_search')
    response = admin_client.get('/profiles/search', query_string={'q': 'no-such-profile'})
    assert response.status_code == 200
    assert 'No profiles found.' in response.text
    assert 'test_story_5_search' not in response.text


def test_TC22_empty_or_whitespace_search_displays_validation_message(app, admin_client):
    for query in ('', '   '):
        with app.app_context(), pytest.raises(DomainError, match='Search text is required.'):
            UserProfile.searchUserProfiles(query)
        response = admin_client.get('/profiles/search', query_string={'q': query})
        assert response.status_code == 200
        assert 'Search text is required.' in response.text
