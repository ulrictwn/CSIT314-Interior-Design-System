import pytest

pytestmark = pytest.mark.story5


def test_TC19_search_matches_profile_name_without_case_sensitivity(client, seed):
    seed('UniqueCustomerRole')
    response = client.get('/profiles/search', query_string={'q': 'uniquecustomer'})
    assert response.status_code == 200
    assert 'UniqueCustomerRole' in response.get_data(as_text=True)


def test_TC20_search_matches_description(client, seed):
    seed('Designer role', description='Specializes in Scandinavian interiors')
    response = client.get('/profiles/search', query_string={'q': 'Scandinavian'})
    assert response.status_code == 200
    assert 'Designer role' in response.get_data(as_text=True)


def test_TC21_no_matching_profiles_shows_empty_message(client, seed):
    seed()
    response = client.get('/profiles/search', query_string={'q': 'no-such-role'})
    assert response.status_code == 200
    assert 'No profiles found.' in response.get_data(as_text=True)


@pytest.mark.parametrize('query', ['', '   '], ids=['empty', 'whitespace'])
def test_TC22_blank_search_requests_input(client, query):
    response = client.get('/profiles/search', query_string={'q': query})
    assert response.status_code == 200
    assert 'Search text is required.' in response.get_data(as_text=True)
