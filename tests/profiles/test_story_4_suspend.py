import pytest

pytestmark = pytest.mark.story4


def test_TC21_suspend_unassigned_profile_persists_status(seed, submit, snapshot):
    profile_id = seed()
    assert submit(f'/profiles/{profile_id}/suspend', {}).status_code == 302
    assert snapshot(profile_id)['status'] == 'Suspended'


@pytest.mark.parametrize('table_name', ['user_account', 'user_accounts'])
@pytest.mark.parametrize('account_status', ['Active', 'Suspended'])
def test_TC22_assigned_profile_cannot_be_suspended(seed, account_assignment, submit, snapshot, table_name, account_status):
    profile_id = seed()
    account_assignment(profile_id, table_name, account_status)
    response = submit(f'/profiles/{profile_id}/suspend', {})
    assert response.status_code == 400
    assert 'This profile is in use.' in response.get_data(as_text=True)
    assert snapshot(profile_id)['status'] == 'Active'


def test_TC23_update_status_cannot_bypass_assignment_guard(seed, account_assignment, submit, snapshot, profile_data):
    profile_id = seed()
    account_assignment(profile_id)
    before = snapshot(profile_id)
    assert submit(f'/profiles/{profile_id}/update', {**profile_data, 'status': 'Suspended'}).status_code == 400
    assert snapshot(profile_id) == before


def test_TC24_confirmation_and_cancel_do_not_suspend(client, seed, snapshot):
    profile_id = seed()
    page = client.get(f'/profiles/{profile_id}/suspend')
    assert page.status_code == 200
    assert 'href="/profiles">Cancel</a>' in page.get_data(as_text=True)
    client.get('/profiles')
    assert snapshot(profile_id)['status'] == 'Active'


def test_TC25_suspend_missing_profile_returns_404(client):
    assert client.get('/profiles/999999/suspend').status_code == 404
