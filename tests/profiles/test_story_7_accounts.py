import pytest
pytestmark=pytest.mark.story7

def test_TC51_view_account_displays_details_without_password(admin_client,create_account):
    account_id=create_account()
    response=admin_client.get('/accounts/'+account_id)
    assert response.status_code==200
    html=response.get_data(as_text=True)
    for value in [account_id,'customer1','Name customer1','customer1@example.com','+65 6123 4567','Customer','Active']:
        assert value in html
    assert 'Review-Administrator-Password-123' not in html

def test_TC52_missing_account_returns_404(admin_client):
    assert admin_client.get('/accounts/CU999999').status_code==404
