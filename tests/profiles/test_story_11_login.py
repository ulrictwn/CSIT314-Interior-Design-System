import pytest
from infrastructure.database import db
from entity.user_account import UserAccount
pytestmark=pytest.mark.story11

def test_TC37_valid_admin_login_opens_dashboard(admin_client):
    response=admin_client.get('/dashboard')
    assert response.status_code==200
    assert 'Review Administrator' in response.get_data(as_text=True)

@pytest.mark.parametrize('failure',['password','username','nonadmin','suspended-account','suspended-profile'])
def test_T38_invalid_or_unavailable_admin_login_is_generic(app,create_account,set_account_password,sign_in,failure):
    create_account('customer1')
    create_account('secondadmin','User Admin')
    set_account_password('customer1')
    set_account_password('secondadmin')
    username,password='secondadmin','Review-Administrator-Password-123'
    if failure=='password':password='Incorrect-Password-123'
    if failure=='username':username='missing-user'
    if failure=='nonadmin':username='customer1'
    with app.app_context():
        if failure=='suspended-account':UserAccount.getByUsername('secondadmin').status='Suspended'
        if failure=='suspended-profile':UserAccount.getByUsername('secondadmin').profile.status='Suspended'
        db.session.commit()
    client,response=sign_in(username,password)
    assert response.status_code==400
    assert 'Invalid login details' in response.get_data(as_text=True)
    assert client.get('/dashboard').status_code==403
