"""The approved classroom demo exposes the story flows without security gates."""
import pytest

from entity.accounts.user_account import UserAccount
from entity.profile.user_profile import UserProfile
from infrastructure.database import db


@pytest.mark.parametrize('path', ['/dashboard', '/profiles', '/profiles/create', '/profiles/search',
                                   '/accounts', '/accounts/create', '/accounts/search'])
def test_story_pages_are_available_without_login(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert 'Content-Security-Policy' not in page.headers
    assert 'name="csrf_token"' not in page.get_data(as_text=True)


def test_profile_create_update_and_suspend_work_without_login_or_csrf(app, client):
    data = dict(profileName='  Demo Role  ', description='  Demo description  ', status='Active', permissions=[])
    assert client.post('/profiles/create', data=data).status_code == 302
    with app.app_context():
        profile = UserProfile.getProfile('Demo Role')
        profile_id = profile.profile_id
        assert profile.description == 'Demo description'
    assert client.post(f'/profiles/{profile_id}/update', data=dict(
        profileName='Edited Role', description='Edited description', permissions=[])).status_code == 302
    assert client.post(f'/profiles/{profile_id}/suspend').status_code == 302
    with app.app_context():
        profile = UserProfile.getUserProfile(profile_id)
        assert profile.name == 'Edited Role' and profile.status == 'Suspended'


def test_account_flow_works_without_login_csrf_or_permission_selection(app, client, seed):
    profile_id = seed('Demo', permissions=[])
    data = dict(username='  demouser  ', full_name='  Demo User  ', email=' DEMO@EXAMPLE.COM ',
                phone_number='+65 6123 4567', profile_id=profile_id)
    assert client.post('/accounts/create', data=data).status_code == 302
    with app.app_context():
        account = UserAccount.getByUsername('demouser')
        account_id = account.account_id
        assert account.email == 'demo@example.com' and not account.has_password
    assert client.post(f'/accounts/{account_id}/update', data=dict(
        full_name='Edited Demo', email='edited@example.com', profile_id=profile_id)).status_code == 302
    assert client.post(f'/accounts/{account_id}/suspend').status_code == 302
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        assert account.full_name == 'Edited Demo' and account.status == 'Suspended'
        assert not account.has_password


def test_final_admin_can_be_suspended_in_the_demo(app, admin_client):
    assert admin_client.post('/accounts/101/suspend').status_code == 302
    with app.app_context():
        assert UserAccount.getUserAccount('101').status == 'Suspended'
    assert app.test_client().get('/accounts').status_code == 200


def test_profile_permissions_are_saved_data_without_access_gates(app, admin_client):
    with app.app_context():
        profile_id = UserProfile.getProfile('User Admin').profile_id
    assert admin_client.post(f'/profiles/{profile_id}/update', data=dict(
        profileName='Demo Admin', description='Demonstration role', permissions=[])).status_code == 302
    with app.app_context():
        profile = UserProfile.getUserProfile(profile_id)
        assert profile.name == 'Demo Admin' and profile.permissions == []
    client = app.test_client()
    assert client.get('/profiles/create').status_code == 200
    assert client.get('/accounts/create').status_code == 200
