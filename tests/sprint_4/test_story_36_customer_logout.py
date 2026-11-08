"""Sprint 4, user story 36: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint4, pytest.mark.story36]


def test_customer_logout_clears_login_and_returns_to_login_page(client, customer_account):
    with client.session_transaction() as session:
        session['account_id'] = customer_account
    response = client.post('/customer/logout')
    assert response.status_code == 302
    assert response.location == '/customer/login'
    with client.session_transaction() as session:
        assert 'account_id' not in session
