"""Sprint 3, user story 18: one successful workflow through BCE."""

import pytest

pytestmark = [pytest.mark.sprint3, pytest.mark.story18]


def test_TC35_interior_designer_login_opens_dashboard(client, create_account, credentials):
    guest = client.get('/designer')
    assert guest.status_code == 302 and guest.location == '/designer/login'
    invalid = client.post('/designer/login', json=dict(username='   ', password=''))
    assert invalid.status_code == 400
    assert set(invalid.json['errors']) == {'username', 'password'}
    with client.session_transaction() as session:
        assert 'account_id' not in session
    account_id = create_account(credentials['username'], 'Interior Designer', credentials['password'])
    response = client.post('/designer/login', json=credentials)
    assert response.status_code == 302
    assert response.location == '/designer'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/designer').status_code == 200
    for path in ('/dashboard', '/customer', '/manager'):
        assert client.get(path).status_code == 403
