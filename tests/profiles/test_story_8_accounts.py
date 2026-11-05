import pytest
from entity.accounts.user_account import UserAccount
from entity.profile.user_profile import UserProfile
pytestmark=pytest.mark.story8

def test_TC30_update_preserves_id_username_password_and_status(app,create_account,submit):
    account_id=create_account()
    with app.app_context():
        pid=UserProfile.getProfile('Interior Designer').profile_id
        original_hash=UserAccount.getUserAccount(account_id).password_hash
    data=dict(full_name='Updated Name',email='updated@example.com',profile_id=pid,username='forged',status='Suspended')
    assert submit(f'/accounts/{account_id}/update',data).status_code==302
    with app.app_context():
        account=UserAccount.getUserAccount(account_id)
        assert (account.account_id,account.username,account.status,account.password_hash)==('202','customer1','Active',original_hash)
        assert (account.full_name,account.email,account.profile_id)==('Updated Name','updated@example.com',pid)

def test_TC31_invalid_update_preserves_values(app,create_account,submit):
    account_id=create_account()
    with app.app_context():pid=UserProfile.getProfile('Customer').profile_id
    assert submit(f'/accounts/{account_id}/update',dict(full_name='New Name',email='not-an-email',profile_id=pid)).status_code==400
    with app.app_context():assert UserAccount.getUserAccount(account_id).full_name=='Name customer1'

def test_TC32_cancel_is_navigation_and_does_not_update(app,admin_client,create_account):
    account_id=create_account()
    html=admin_client.get(f'/accounts/{account_id}/update').get_data(as_text=True)
    assert 'href="/accounts">Cancel</a>' in html
    admin_client.get('/accounts')
    with app.app_context():assert UserAccount.getUserAccount(account_id).full_name=='Name customer1'

def test_TC33_demo_allows_reassigning_admin_profile(app,admin_client,submit):
    with app.app_context():pid=UserProfile.getProfile('Customer').profile_id
    response=submit('/accounts/101/update',dict(full_name='Admin',email='admin@example.com',profile_id=pid))
    assert response.status_code==302
    with app.app_context():
        assert UserAccount.getUserAccount('101').profile_id == pid
