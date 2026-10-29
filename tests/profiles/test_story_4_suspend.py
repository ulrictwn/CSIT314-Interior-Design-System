import pytest

pytestmark = pytest.mark.story4


def test_TC17_suspend_unassigned_profile_persists_status(seed, submit, snapshot):
    profile_id = seed()
    assert submit(f'/profiles/{profile_id}/suspend', {}).status_code == 302
    assert snapshot(profile_id)['status'] == 'Suspended'


@pytest.mark.parametrize('table_name', ['user_account', 'user_accounts'])
@pytest.mark.parametrize('account_status', ['Active', 'Suspended'])
def test_TC18_assigned_profile_cannot_be_suspended(seed, account_assignment, submit, snapshot, table_name, account_status):
    profile_id = seed()
    account_assignment(profile_id, table_name, account_status)
    response = submit(f'/profiles/{profile_id}/suspend', {})
    assert response.status_code == 400
    assert 'This profile is in use.' in response.get_data(as_text=True)
    assert snapshot(profile_id)['status'] == 'Active'
