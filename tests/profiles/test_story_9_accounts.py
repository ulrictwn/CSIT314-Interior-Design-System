import pytest
from entity.user_account import UserAccount
pytestmark=pytest.mark.story9

def test_TC57_suspend_retains_data_and_rejects_repeated_suspension(app,create_account,submit):
    account_id=create_account()
    assert submit(f'/accounts/{account_id}/suspend',{}).status_code==302
    response=submit(f'/accounts/{account_id}/suspend',{})
    assert response.status_code==400
    assert 'This account is already suspended' in response.get_data(as_text=True)
    with app.app_context():
        account=UserAccount.getUserAccount(account_id)
        assert account.status=='Suspended' and account.email=='customer1@example.com'

def test_TC58_suspension_ends_existing_access(app,create_account,sign_in,submit):
    account_id=create_account('secondadmin','User Admin')
    other,response=sign_in('secondadmin')
    assert response.status_code==302
    assert other.get('/dashboard').status_code==200
    assert submit(f'/accounts/{account_id}/suspend',{}).status_code==302
    assert other.get('/dashboard').status_code==403
