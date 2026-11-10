"""Sprint 4, user story 35: one successful workflow through BCE."""
from unittest.mock import patch

import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story35]


def test_customer_login_opens_dashboard(client, create_account, credentials):
    guest = client.get('/customer')
    assert guest.status_code == 302 and guest.location == '/customer/login'
    with patch('boundary.customer.customer_login_page.CustomerLoginController.login', side_effect=AssertionError('Invalid fields reached controller')):
        invalid = client.post('/customer/login', json=dict(username='   ', password=''))
    assert invalid.status_code == 400
    assert set(invalid.json['errors']) == {'username', 'password'}
    account_id = create_account(credentials['username'], 'Customer', credentials['password'])
    response = client.post('/customer/login', json=credentials)
    assert response.status_code == 302
    assert response.location == '/customer'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/customer').status_code == 200
    for path in ('/dashboard', '/designer', '/manager'):
        assert client.get(path).status_code == 403
