import pytest
from entity.user_account import UserAccount
from entity.user_profile import UserProfile
from infrastructure.database import db

pytestmark = pytest.mark.story6

@pytest.mark.parametrize('role,prefix', [('Customer','CU101'),('Interior Designer','ID101'),('Platform Management','PM101'),('User Admin','UA102')])
def test_TC46_account_id_matches_assigned_role(create_account, role, prefix):
    assert create_account('newuser',role)==prefix

def test_TC47_ids_increment_and_password_is_hashed(app, create_account):
    assert create_account('customer1')=='CU101'
    assert create_account('customer2')=='CU102'
    with app.app_context():
        account=UserAccount.getByUsername('customer1')
        assert account.status=='Active' and account.phone_number=='+65 6123 4567'
        assert account.password_hash!='Review-Administrator-Password-123'
        assert account.check_password('Review-Administrator-Password-123')

def test_TC48_duplicate_username_is_rejected(app, create_account, submit):
    create_account('customer1')
    with app.app_context():profile=UserProfile.getProfile('Customer').profile_id
    response=submit('/accounts/create',dict(username='CUSTOMER1',password='Review-Administrator-Password-123',confirm_password='Review-Administrator-Password-123',full_name='Duplicate',email='unique@example.com',phone_number='+65 6123 4567',profile_id=profile))
    assert response.status_code==400
    with app.app_context():assert len(UserAccount.searchUserAccounts())==2

@pytest.mark.parametrize('missing',['username','password','full_name','email','phone_number','profile_id'])
def test_TC49_invalid_create_does_not_save(app, admin_client, submit, missing):
    with app.app_context():profile=UserProfile.getProfile('Customer').profile_id
    data=dict(username='customer1',password='Review-Administrator-Password-123',confirm_password='Review-Administrator-Password-123',full_name='Customer One',email='customer@example.com',phone_number='+65 6123 4567',profile_id=profile)
    data[missing]=''
    assert submit('/accounts/create',data).status_code==400
    with app.app_context():assert UserAccount.getByUsername('customer1') is None

def test_TC50_inactive_profile_cannot_be_assigned(app, admin_client, seed, submit):
    pid=seed('Retired',status='Suspended')
    data=dict(username='customer1',password='Review-Administrator-Password-123',confirm_password='Review-Administrator-Password-123',full_name='Customer One',email='customer@example.com',phone_number='+65 6123 4567',profile_id=pid)
    assert submit('/accounts/create',data).status_code==400
