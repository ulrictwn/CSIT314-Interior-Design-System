import pytest

pytestmark = pytest.mark.story12


def test_TC39_logout_clears_current_browser_and_keeps_other_login(app, admin_client, sign_in):
    other, response = sign_in('admin')
    assert response.status_code == 302
    response = admin_client.post('/logout')
    assert response.status_code == 302 and response.headers['Location'].endswith('/login')
    with admin_client.session_transaction() as browser:
        assert 'account_id' not in browser
    # Demo pages stay accessible, but the current login display is cleared.
    page = admin_client.get('/dashboard')
    assert page.status_code == 200 and 'Review Administrator' not in page.get_data(as_text=True)
    assert 'Review Administrator' in other.get('/dashboard').get_data(as_text=True)
