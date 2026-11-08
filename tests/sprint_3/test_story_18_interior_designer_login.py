"""Sprint 3, user story 18: one successful workflow through BCE."""
import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story18]


def test_interior_designer_login_opens_dashboard(client, create_account, credentials):
    account_id = create_account(credentials['username'], 'Interior Designer', credentials['password'])
    response = client.post('/designer/login', json=credentials)
    assert response.status_code == 302
    assert response.location == '/designer'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/designer').status_code == 200
