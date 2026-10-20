import re
import pytest
pytestmark=pytest.mark.story12

def test_TC65_logout_revokes_current_cookie_and_keeps_other_login(app,admin_client,sign_in):
    other,response=sign_in('admin')
    assert response.status_code==302
    old_cookie=admin_client.get_cookie('session').value
    page=admin_client.get('/dashboard').get_data(as_text=True)
    token=re.search(r'name="csrf_token"[^>]*value="([^"]+)"',page).group(1)
    response=admin_client.post('/logout',data={'csrf_token':token})
    assert response.status_code==302 and response.headers['Location'].endswith('/login')
    assert admin_client.get('/dashboard').status_code==403
    replay=app.test_client();replay.set_cookie('session',old_cookie)
    assert replay.get('/dashboard').status_code==403
    assert other.get('/dashboard').status_code==200

def test_TC66_logout_requires_post_and_csrf(admin_client):
    assert admin_client.get('/logout').status_code==405
    assert admin_client.post('/logout',data={}).status_code==400
    assert admin_client.get('/dashboard').status_code==200
