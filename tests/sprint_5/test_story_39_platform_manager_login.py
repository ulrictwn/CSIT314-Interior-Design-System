"""Sprint 5, user story 39: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story39]


def test_platform_manager_login_opens_dashboard(client, create_account, credentials):
    account_id = create_account(credentials['username'], 'Platform Management', credentials['password'])
    response = client.post('/manager/login', json=credentials)
    assert response.status_code == 302
    assert response.location == '/manager'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/manager').status_code == 200
