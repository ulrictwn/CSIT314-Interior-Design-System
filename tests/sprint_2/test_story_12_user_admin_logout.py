"""Sprint 2, user story 12: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story12]


def test_user_admin_logout_clears_login_and_returns_to_login_page(client, create_account):
    account_id = create_account('admin', 'User Admin')
    with client.session_transaction() as session:
        session['account_id'] = account_id
    response = client.post('/logout')
    assert response.status_code == 302
    assert response.location == '/login'
    with client.session_transaction() as session:
        assert 'account_id' not in session
    protected = client.get('/dashboard')
    assert protected.status_code == 302 and protected.location == '/login'
