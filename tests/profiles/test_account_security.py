import pytest

from entity.user_account import UserAccount
from entity.user_profile import UserProfile
from infrastructure.database import db

pytestmark = pytest.mark.security


@pytest.mark.parametrize('operation', ['create', 'view', 'update', 'suspend', 'search'])
def test_TC67_account_pages_require_their_permission(app, admin_client, create_account, operation):
    account_id = create_account()
    with app.app_context():
        profile = UserProfile.getProfile('User Admin')
        profile.permissions = [p for p in profile.permissions if p != 'account.' + operation]
        db.session.commit()
    urls = {'create': '/accounts/create', 'view': f'/accounts/{account_id}',
            'update': f'/accounts/{account_id}/update', 'suspend': f'/accounts/{account_id}/suspend',
            'search': '/accounts/search'}
    assert admin_client.get(urls[operation]).status_code == 403


@pytest.mark.parametrize('operation', ['create', 'update', 'suspend'])
def test_TC68_account_modifications_require_csrf(app, admin_client, create_account, operation):
    account_id = create_account()
    url = '/accounts/create' if operation == 'create' else f'/accounts/{account_id}/{operation}'
    assert admin_client.post(url, data={}).status_code == 400
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        assert account.status == 'Active' and account.full_name == 'Name customer1'
        assert db.session.query(UserAccount).count() == 2


@pytest.mark.parametrize('change', ['rename', 'remove_permission', 'suspend'])
def test_TC69_last_admin_cannot_lose_access_via_profile_update(app, admin_client, submit, change):
    with app.app_context():
        profile = UserProfile.getProfile('User Admin')
        profile_id = profile.profile_id
        permissions = list(profile.permissions)
    data = dict(profileName='User Admin', description='Administration', status='Active', permissions=permissions)
    if change == 'rename':
        data['profileName'] = 'Former Admin'
    elif change == 'remove_permission':
        data['permissions'].remove('account.create')
    else:
        data['status'] = 'Suspended'
    response = submit(f'/profiles/{profile_id}/update', data)
    assert response.status_code == 400
    with app.app_context():
        profile = UserProfile.getUserProfile(profile_id)
        assert profile.name == 'User Admin' and profile.status == 'Active'
        assert 'account.create' in profile.permissions
