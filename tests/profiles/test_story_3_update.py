import pytest

pytestmark = pytest.mark.story3


def test_TC14_update_form_contains_current_values(client, seed):
    profile_id = seed('Customer', description='Original description')
    page = client.get(f'/profiles/{profile_id}/update')
    assert page.status_code == 200
    html = page.get_data(as_text=True)
    assert 'value="Customer"' in html
    assert 'Original description' in html
    assert 'checked' in html


def test_TC15_update_persists_fields_and_permissions(seed, submit, snapshot, profile_data):
    profile_id = seed()
    values = {**profile_data, 'profileName': 'Designer', 'description': 'Updated description', 'permissions': ['profile.update']}
    assert submit(f'/profiles/{profile_id}/update', values).status_code == 302
    saved = snapshot(profile_id)
    assert (saved['name'], saved['description'], saved['permissions']) == ('Designer', 'Updated description', ['profile.update'])


def test_TC16_duplicate_update_preserves_original_record(seed, submit, snapshot, profile_data):
    profile_id = seed('Customer')
    seed('Designer')
    before = snapshot(profile_id)
    assert submit(f'/profiles/{profile_id}/update', {**profile_data, 'profileName': 'designer'}).status_code == 400
    assert snapshot(profile_id) == before


@pytest.mark.parametrize('field', ['profileName', 'description', 'status'])
def test_TC17_invalid_update_preserves_original_record(seed, submit, snapshot, profile_data, field):
    profile_id = seed()
    before = snapshot(profile_id)
    assert submit(f'/profiles/{profile_id}/update', {**profile_data, field: ''}).status_code == 400
    assert snapshot(profile_id) == before


def test_TC18_update_missing_profile_returns_404(client):
    assert client.get('/profiles/999999/update').status_code == 404


def test_TC19_update_can_keep_its_own_name(seed, submit, snapshot, profile_data):
    profile_id = seed()
    assert submit(f'/profiles/{profile_id}/update', profile_data).status_code == 302
    assert snapshot(profile_id)['name'] == 'Customer'


def test_TC20_cancel_update_leaves_database_unchanged(client, seed, snapshot):
    profile_id = seed()
    before = snapshot(profile_id)
    page = client.get(f'/profiles/{profile_id}/update').get_data(as_text=True)
    assert 'href="/profiles">Cancel</a>' in page
    client.get('/profiles')
    assert snapshot(profile_id) == before
