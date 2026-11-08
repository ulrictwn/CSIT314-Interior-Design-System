"""Story 4: TC17–TC18 from the Word document."""
import pytest
from entity.accounts.user_account import UserAccount

pytestmark = [pytest.mark.sprint1, pytest.mark.story4]


def test_TC17_unassigned_profile_can_be_suspended_and_status_is_saved(admin_client, seed_profile, profile_snapshot):
    profile_id = seed_profile('Test_Story_4_suspend')
    response = admin_client.post(f'/profiles/{profile_id}/suspend', follow_redirects=True)
    assert response.status_code == 200
    assert 'suspended successfully' in response.text
    assert profile_snapshot(profile_id)['status'] == 'Suspended'


def test_TC18_assigned_profile_cannot_be_suspended(app, admin_client, customer_account, profile_snapshot):
    with app.app_context():
        profile_id = UserAccount.getUserAccount(customer_account).profile_id
    response = admin_client.post(f'/profiles/{profile_id}/suspend')
    assert response.status_code == 400
    assert 'This profile is in use.' in response.text
    assert profile_snapshot(profile_id)['status'] == 'Active'
