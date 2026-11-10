"""Sprint 5, user story 39: one successful workflow through BCE."""

import pytest

pytestmark = [pytest.mark.sprint5, pytest.mark.story39]


def test_TC56_platform_manager_login_opens_dashboard(client, create_account, credentials):
    guest = client.get('/manager')
    assert guest.status_code == 302 and guest.location == '/manager/login'
    invalid = client.post('/manager/login', json=dict(username='   ', password=''))
    assert invalid.status_code == 400
    assert set(invalid.json['errors']) == {'username', 'password'}
    with client.session_transaction() as session:
        assert 'account_id' not in session
    account_id = create_account(credentials['username'], 'Platform Management', credentials['password'])
    response = client.post('/manager/login', json=credentials)
    assert response.status_code == 302
    assert response.location == '/manager'
    with client.session_transaction() as session:
        assert session['account_id'] == account_id
    assert client.get('/manager').status_code == 200
    for path in ('/dashboard', '/designer', '/customer'):
        assert client.get(path).status_code == 403
