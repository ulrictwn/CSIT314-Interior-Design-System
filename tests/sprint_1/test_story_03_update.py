"""Story 3: its Checks list defines TC12–TC16, despite the broader ID heading."""
import pytest

pytestmark = [pytest.mark.sprint1, pytest.mark.story3]


def test_TC12_update_form_displays_existing_fields_and_selected_permissions(admin_client, seed_profile, form_controls):
    profile_id = seed_profile('test_story_3_update', description='This profile is created for TC12 to TC18.',
                              permissions=['profile.search'])
    response = admin_client.get(f'/profiles/{profile_id}/update')
    assert response.status_code == 200
    assert 'value="test_story_3_update"' in response.text
    assert 'This profile is created for TC12 to TC18.' in response.text
    selected = {item['value'] for item in form_controls(response.text)
                if item.get('name') == 'permissions' and 'checked' in item}
    assert selected == {'profile.search'}


def test_TC13_changes_are_saved_accurately(admin_client, seed_profile, profile_snapshot):
    profile_id = seed_profile('test_story_3_update')
    response = admin_client.post(f'/profiles/{profile_id}/update', data=dict(
        profileName='Updated Designer', description='Updated description', permissions=['profile.update']),
        follow_redirects=True)
    assert response.status_code == 200
    assert 'User profile updated successfully.' in response.text
    assert profile_snapshot(profile_id) == dict(name='Updated Designer', description='Updated description',
                                               status='Active', permissions=['profile.update'])


def test_TC14_duplicate_name_is_rejected_and_original_record_is_unchanged(admin_client, seed_profile, profile_snapshot):
    profile_id = seed_profile('Customer')
    seed_profile('Designer')
    before = profile_snapshot(profile_id)
    response = admin_client.post(f'/profiles/{profile_id}/update', data=dict(
        profileName='designer', description='Unsaved change', permissions=[]))
    assert response.status_code == 400
    assert profile_snapshot(profile_id) == before


def test_TC15_missing_required_update_fields_are_rejected(admin_client, seed_profile, profile_snapshot):
    profile_id = seed_profile()
    before = profile_snapshot(profile_id)
    values = dict(profileName='Updated role', description='Updated description', permissions=[])
    for field in ('profileName', 'description'):
        response = admin_client.post(f'/profiles/{profile_id}/update', data={**values, field: ''})
        assert response.status_code == 400, field
        assert profile_snapshot(profile_id) == before


def test_TC16_updating_nonexistent_profile_returns_error(admin_client):
    assert admin_client.get('/profiles/999999/update').status_code == 404
    response = admin_client.post('/profiles/999999/update', data=dict(
        profileName='Missing role', description='No such profile', permissions=[]))
    assert response.status_code == 404
