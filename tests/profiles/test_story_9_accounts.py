import pytest
from entity.accounts.user_account import UserAccount
pytestmark=pytest.mark.story9

def test_TC34_suspend_retains_data_and_rejects_repeated_suspension(app,create_account,submit):
    account_id=create_account()
    assert submit(f'/accounts/{account_id}/suspend',{}).status_code==302
    response=submit(f'/accounts/{account_id}/suspend',{})
    assert response.status_code==400
    assert 'This account is already suspended' in response.get_data(as_text=True)
    with app.app_context():
        account=UserAccount.getUserAccount(account_id)
        assert account.status=='Suspended' and account.email=='customer1@example.com'
