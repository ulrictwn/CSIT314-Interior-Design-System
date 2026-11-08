"""Sprint 4, user story 35: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story35]


def test_customer_login_opens_dashboard(client, create_account, credentials):
    account_id = create_account(credentials['username'], 'Customer', credentials['password'])
    response = client.post('/customer/login', json=credentials)
    assert response.status_code == 302
    assert response.location == '/customer'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/customer').status_code == 200
