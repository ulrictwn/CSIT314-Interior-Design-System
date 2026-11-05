from unittest.mock import Mock
import pytest
from sqlalchemy import inspect

from boundary.designer.interior_designer_login_page import InteriorDesignerLoginPage
from boundary.designer.interior_designer_logout_page import InteriorDesignerLogoutPage
from control.designer.interior_designer_login_controller import InteriorDesignerLoginController
from entity.accounts.user_account import UserAccount
from entity.projects.interior_design_project import InteriorDesignProject
from entity.company.company_profile import CompanyProfile
from infrastructure.database import db
from infrastructure.migrations import upgrade_database

PASSWORD = 'Designer-Demo-Password-123'


@pytest.mark.story18
@pytest.mark.story19
def test_designer_login_context_and_logout(client, designer_accounts, company_data):
    owner, other = designer_accounts
    response = client.post('/designer/login', json=dict(username=' designer1 ', password=PASSWORD))
    assert response.status_code == 302 and response.headers['Location'] == '/designer'
    assert client.get('/designer').json['accountId'] == owner
    # Account context flows from the basic session, not an added event argument.
    assert client.post('/designer/company/create', json=company_data).status_code == 201
    assert client.get('/designer/company').json['profile']['accountId'] == owner
    response = client.post('/designer/logout')
    assert response.status_code == 302 and response.headers['Location'] == '/designer/login'
    with client.session_transaction() as browser:
        assert 'account_id' not in browser
    assert client.get('/designer/company').status_code == 400
    assert client.get('/designer/company', query_string={'accountId': owner}).status_code == 200


@pytest.mark.parametrize('username,password', [('designer1','incorrect'), ('missing', PASSWORD), ('designer2', PASSWORD)])
def test_designer_login_rejects_unmatched_or_unconfigured_credentials(client, designer_accounts, username, password):
    response = client.post('/designer/login', json=dict(username=username, password=password))
    assert response.status_code == 400 and response.json['message'] == 'Invalid login details'
    assert password not in response.get_data(as_text=True)


@pytest.mark.parametrize('username,password', [('',PASSWORD), (None,PASSWORD), ('x'*81,PASSWORD),
                                             ('designer1',''), ('designer1','x'*129)])
def test_designer_login_fields_are_checked_before_controller(monkeypatch, app, username, password):
    login = Mock(side_effect=AssertionError('Invalid login reached the controller'))
    monkeypatch.setattr(InteriorDesignerLoginController, 'login', login)
    with app.test_request_context('/designer/login', method='POST'):
        page = InteriorDesignerLoginPage()
        assert page.onLogin(username, password) is None
        assert page.rendered_page[1] == 400
    login.assert_not_called()


@pytest.mark.parametrize('change', ['account', 'profile', 'role'])
def test_designer_login_checks_saved_status_and_role(app, client, designer_accounts, seed, change):
    owner, _ = designer_accounts
    with app.app_context():
        account = UserAccount.getUserAccount(owner)
        if change == 'account':
            account.status = 'Suspended'
        elif change == 'profile':
            account.profile.status = 'Suspended'
        else:
            from entity.profile.user_profile import UserProfile
            role = UserProfile(name='User Admin', description='Admin', status='Active', permissions=[])
            db.session.add(role)
            db.session.flush()
            account.profile_id = role.profile_id
        db.session.commit()
    response = client.post('/designer/login', json=dict(username='designer1', password=PASSWORD))
    assert response.status_code == 400


@pytest.mark.story18
@pytest.mark.story19
def test_designer_events_are_void(app, designer_accounts):
    with app.test_request_context('/designer/login', method='POST'):
        page = InteriorDesignerLoginPage()
        assert page.onLogin('designer1', PASSWORD) is None
        assert page.rendered_page.status_code == 302
        logout = InteriorDesignerLogoutPage()
        assert logout.logout() is None
        assert logout.rendered_page.headers['Location'] == '/designer/login'


@pytest.mark.database
def test_upgrade_adds_new_tables_and_preserves_accounts(app, designer_accounts):
    owner, _ = designer_accounts
    with app.app_context():
        account = UserAccount.getUserAccount(owner)
        before = (account.username, account.email, account.password_hash)
        db.session.remove()
        # Disposable test database only: simulate a pre-Stories-13–29 installation.
        InteriorDesignProject.__table__.drop(db.engine)
        CompanyProfile.__table__.drop(db.engine)
        upgrade_database()
        assert {'company_profile', 'interior_design_project'}.issubset(inspect(db.engine).get_table_names())
        account = UserAccount.getUserAccount(owner)
        assert (account.username, account.email, account.password_hash) == before
