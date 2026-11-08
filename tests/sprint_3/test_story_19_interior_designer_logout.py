"""Sprint 3, user story 19: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story19]


def test_interior_designer_logout_clears_login_and_returns_to_login_page(client, designer_account):
    with client.session_transaction() as session:
        session['account_id'] = designer_account
    response = client.post('/designer/logout')
    assert response.status_code == 302
    assert response.location == '/designer/login'
    with client.session_transaction() as session:
        assert 'account_id' not in session
