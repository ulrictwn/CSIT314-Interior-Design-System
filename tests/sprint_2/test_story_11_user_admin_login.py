"""Sprint 2, user story 11: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint2, pytest.mark.story11]


def test_user_admin_login_opens_dashboard(client, create_account, credentials):
    account_id = create_account(credentials['username'], 'User Admin', credentials['password'])
    response = client.post('/login', data=credentials)
    assert response.status_code == 302
    assert response.location == '/dashboard'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/dashboard').status_code == 200
