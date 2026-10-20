import pytest

pytestmark = pytest.mark.story5


def test_TC26_search_matches_profile_name_without_case_sensitivity(client, seed):
    seed('UniqueCustomerRole')
    response = client.get('/profiles/search', query_string={'q': 'uniquecustomer'})
    assert response.status_code == 200
    assert 'UniqueCustomerRole' in response.get_data(as_text=True)


def test_TC27_search_matches_description(client, seed):
    seed('Designer role', description='Specializes in Scandinavian interiors')
    response = client.get('/profiles/search', query_string={'q': 'Scandinavian'})
    assert response.status_code == 200
    assert 'Designer role' in response.get_data(as_text=True)


def test_TC28_no_matching_profiles_shows_empty_message(client, seed):
    seed()
    response = client.get('/profiles/search', query_string={'q': 'no-such-role'})
    assert response.status_code == 200
    assert 'No profiles found.' in response.get_data(as_text=True)


@pytest.mark.parametrize('query', ['', '   '], ids=['empty', 'whitespace'])
def test_TC29_blank_search_requests_input(client, query):
    response = client.get('/profiles/search', query_string={'q': query})
    assert response.status_code == 200
    assert 'Search text is required.' in response.get_data(as_text=True)


@pytest.mark.parametrize('literal', ['%', '_'], ids=['percent', 'underscore'])
def test_TC30_search_treats_sql_wildcards_as_literal_text(client, seed, literal):
    seed('Literal' + literal + 'Role')
    seed('UnrelatedRole')
    response = client.get('/profiles/search', query_string={'q': literal})
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Literal' + literal + 'Role' in html
    assert 'UnrelatedRole' not in html


def test_TC31_sql_injection_text_does_not_return_all_records(client, seed):
    seed('UnrelatedRole')
    response = client.get('/profiles/search', query_string={'q': "' OR 1=1 --"})
    assert response.status_code == 200
    assert 'No profiles found.' in response.get_data(as_text=True)
    assert 'UnrelatedRole' not in response.get_data(as_text=True)


def test_TC32_search_input_is_html_escaped(client):
    response = client.get('/profiles/search', query_string={'q': '<script>alert(1)</script>'})
    html = response.get_data(as_text=True)
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '<script>alert(1)</script>' not in html


def test_TC45_search_initially_lists_all_then_filters_same_table(client, seed):
    seed('Customer')
    seed('Designer', description='Interior design role')
    initial = client.get('/profiles/search').get_data(as_text=True)
    assert 'Customer' in initial and 'Designer' in initial
    filtered = client.get('/profiles/search?q=Customer').get_data(as_text=True)
    assert 'Customer' in filtered and 'Designer' not in filtered
