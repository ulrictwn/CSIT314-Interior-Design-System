"""Sprint 5, user story 40: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story40]


def test_platform_manager_logout_clears_login_and_returns_to_login_page(client, create_account):
    account_id = create_account('manager1', 'Platform Management')
    with client.session_transaction() as session:
        session['account_id'] = account_id
    response = client.post('/manager/logout')
    assert response.status_code == 302
    assert response.location == '/manager/login'
    with client.session_transaction() as session:
        assert 'account_id' not in session
    protected = client.get('/manager')
    assert protected.status_code == 302 and protected.location == '/manager/login'
