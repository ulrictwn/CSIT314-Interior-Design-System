"""Account BCE contracts, boundary input validation, and HTML form regressions."""
from html.parser import HTMLParser
from unittest.mock import Mock

import pytest
from flask import g

from boundary.accounts.create_user_account_page import CreateUserAccountPage
from boundary.accounts.view_user_account_page import ViewUserAccountPage
from boundary.accounts.update_user_account_page import UpdateUserAccountPage
from boundary.accounts.suspend_user_account_page import SuspendUserAccountPage
from boundary.accounts.search_user_account_page import SearchUserAccountPage
from control.accounts.create_user_account_controller import CreateUserAccountController
from control.accounts.view_user_account_controller import ViewUserAccountController
from control.accounts.update_user_account_controller import UpdateUserAccountController
from control.accounts.suspend_user_account_controller import SuspendUserAccountController
from control.accounts.search_user_account_controller import SearchUserAccountController
from entity.accounts.user_account import UserAccount, AccountIdCounter
from entity.profile.user_profile import UserProfile
from infrastructure.database import db
from infrastructure.errors import DomainError


class Controls(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.items = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in ('input', 'select', 'option'):
            self.items.append(dict(attrs))

    def value(self, name):
        return next(item['value'] for item in self.items if item.get('name') == name)


@pytest.fixture
def account_data():
    return dict(username='customer1', fullName='Customer One', email='customer@example.com',
                phoneNumber='+65 6123 4567', profileId=1)


@pytest.fixture
def saved_account(app, seed, account_data):
    profile_id = seed('Customer')
    with app.app_context():
        account = UserAccount()
        assert account.createUserAccount(**{**account_data, 'profileId': profile_id}) is True
        return account.account_id, profile_id


def forbid_database(monkeypatch):
    for name in ('execute', 'get', 'add', 'flush', 'commit', 'rollback'):
        monkeypatch.setattr(db.session, name,
            Mock(side_effect=AssertionError('Invalid account data reached the database')))


@pytest.mark.story6
@pytest.mark.parametrize('patch, field', [
    ({'username': ''}, 'username'), ({'username': None}, 'username'),
    ({'username': 'ab'}, 'username'), ({'username': 'x' * 81}, 'username'),
    ({'username': 'has space'}, 'username'),
    ({'fullName': '   '}, 'full_name'), ({'fullName': 'x' * 121}, 'full_name'),
    ({'email': ''}, 'email'), ({'email': 'not-an-email'}, 'email'),
    ({'email': 'x' * 255}, 'email'),
    ({'phoneNumber': ''}, 'phone_number'), ({'phoneNumber': 'letters'}, 'phone_number'),
    ({'phoneNumber': '1'}, 'phone_number'), ({'phoneNumber': '1' * 41}, 'phone_number'),
    ({'profileId': None}, 'profile_id'), ({'profileId': True}, 'profile_id'),
    ({'profileId': 0}, 'profile_id'), ({'profileId': '1'}, 'profile_id'),
    ({'profileId': 2_147_483_648}, 'profile_id'), ({'password': 'short'}, 'password'),
])
def test_create_boundary_validates_before_controller_access(app, monkeypatch, account_data, patch, field):
    from boundary.validation import password_value
    create = Mock(side_effect=AssertionError('Invalid account data reached the controller'))
    monkeypatch.setattr(CreateUserAccountController, 'createUserAccount', create)
    monkeypatch.setattr(CreateUserAccountController, 'activeProfiles', lambda self: [])
    if 'password' in patch:
        # Password entry is currently a trusted CLI boundary, rather than a web field.
        with pytest.raises(DomainError):
            password_value(patch['password'])
    else:
        with app.test_request_context('/accounts/create', method='POST'):
            page = CreateUserAccountPage()
            assert page.clickCreate(**{**account_data, **patch}) is None
            assert field in page.field_errors
            assert page.rendered_page[1] == 400
    create.assert_not_called()


@pytest.mark.story6
def test_create_boundary_normalizes_and_entity_saves_without_password(app, seed, submit):
    profile_id = seed('Customer')
    response = submit('/accounts/create', dict(username='  customer1  ', full_name='  Customer One  ',
        email=' CUSTOMER@EXAMPLE.COM ', phone_number=' +65 6123 4567 ', profile_id=profile_id))
    assert response.status_code == 302
    with app.app_context():
        saved = UserAccount.getByUsername('customer1')
        assert (saved.full_name, saved.email, saved.phone_number) == (
            'Customer One', 'customer@example.com', '+65 6123 4567')
        assert saved.account_id == f'{profile_id}01' and saved.status == 'Active'
        assert not saved.has_password


@pytest.mark.story6
@pytest.mark.parametrize('field, patch', [
    ('username', {'username': 'CUSTOMER1', 'email': 'other@example.com'}),
    ('email', {'username': 'customer2', 'email': 'CUSTOMER@EXAMPLE.COM'}),
])
def test_create_duplicate_does_not_consume_account_number(app, saved_account, account_data, field, patch):
    _, profile_id = saved_account
    with app.app_context():
        before = db.session.get(AccountIdCounter, '*').next_number
        operation = UserAccount()
        assert operation.createUserAccount(**{**account_data, 'profileId': profile_id, **patch}) is False
        assert field in operation.field_errors
        assert db.session.get(AccountIdCounter, '*').next_number == before
        assert len(UserAccount.searchUserAccounts()) == 1


@pytest.mark.story6
def test_create_unique_constraint_failure_rolls_back_number_and_allows_retry(app, saved_account, account_data, monkeypatch):
    _, profile_id = saved_account
    with app.app_context():
        monkeypatch.setattr(UserAccount, '_email_exists', lambda *args: False)
        operation = UserAccount()
        assert operation.createUserAccount(**{**account_data, 'username': 'customer2', 'profileId': profile_id}) is False
        assert 'registered' in operation.error_message
        assert db.session.get(AccountIdCounter, '*').next_number == 2
        assert UserAccount().createUserAccount(**{**account_data, 'username': 'customer2',
            'email': 'second@example.com', 'profileId': profile_id}) is True
        assert UserAccount.getByUsername('customer2').account_id == f'{profile_id}02'


@pytest.mark.story6
def test_entity_rejects_inactive_profile_without_allocating_id(app, seed, account_data):
    profile_id = seed('Retired', status='Suspended')
    with app.app_context():
        operation = UserAccount()
        assert operation.createUserAccount(**{**account_data, 'profileId': profile_id}) is False
        assert operation.field_errors['profile_id']
        assert UserAccount.searchUserAccounts() == []
        assert db.session.get(AccountIdCounter, '*') is None


@pytest.mark.story7
@pytest.mark.parametrize('account_id', [None, True, 42, '', '   ', 'x' * 33])
def test_view_boundary_validates_account_id_before_lookup(app, monkeypatch, account_id):
    lookup = Mock(side_effect=AssertionError('Invalid account ID reached the controller'))
    monkeypatch.setattr(ViewUserAccountController, 'getUserAccount', lookup)
    with app.test_request_context('/accounts/invalid'):
        page = ViewUserAccountPage()
        assert page.onView(account_id) is None
        assert page.rendered_page[1] == 404
    lookup.assert_not_called()


@pytest.mark.story8
@pytest.mark.parametrize('patch', [
    {'accountId': None}, {'accountId': 42}, {'accountId': 'x' * 33},
    {'fullName': ''}, {'fullName': 'x' * 121}, {'email': None}, {'email': 'invalid'},
    {'profileId': None}, {'profileId': True}, {'profileId': '1'},
])
def test_update_boundary_validates_before_controller_access(app, monkeypatch, patch):
    from types import SimpleNamespace
    update = Mock(side_effect=AssertionError('Invalid account update reached the controller'))
    monkeypatch.setattr(UpdateUserAccountController, 'updateUserAccount', update)
    monkeypatch.setattr(UpdateUserAccountController, 'getUserAccount',
        lambda self, account_id: SimpleNamespace(account_id='101', username='original', phone_number='+65 6123 4567'))
    monkeypatch.setattr(UpdateUserAccountController, 'activeProfiles', lambda self: [])
    data = dict(accountId='101', fullName='Updated Name', email='updated@example.com', profileId=1)
    with app.test_request_context('/accounts/101/update', method='POST'):
        page = UpdateUserAccountPage()
        assert page.onUpdate(**{**data, **patch}) is None
        assert page.error_message
        assert page.rendered_page[1] in (400, 404)
    update.assert_not_called()


@pytest.mark.story8
def test_update_boundary_normalizes_and_entity_preserves_immutable_values(app, saved_account, submit):
    account_id, profile_id = saved_account
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        before = (account.account_id, account.username, account.password_hash,
                  account.status, account.phone_number, account.auth_version)
    response = submit(f'/accounts/{account_id}/update', dict(full_name='  Changed Name  ',
        email=' CHANGED@EXAMPLE.COM ', profile_id=profile_id))
    assert response.status_code == 302
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        assert (account.full_name, account.email) == ('Changed Name', 'changed@example.com')
        assert (account.account_id, account.username, account.password_hash,
                account.status, account.phone_number, account.auth_version) == before


@pytest.mark.story9
def test_suspend_entity_returns_boolean_preserves_data_and_rejects_repeat(app, saved_account):
    account_id, _ = saved_account
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        before = (account.username, account.full_name, account.email, account.phone_number, account.password_hash)
        version = account.auth_version
        assert UserAccount().suspendUserAccount(account_id) is True
        db.session.expire_all()
        account = UserAccount.getUserAccount(account_id)
        assert account.status == 'Suspended' and account.auth_version == version
        assert (account.username, account.full_name, account.email, account.phone_number, account.password_hash) == before
        operation = UserAccount()
        assert operation.suspendUserAccount(account_id) is False
        assert operation.error_message == 'This account is already suspended'
        assert UserAccount.getUserAccount(account_id).auth_version == version


@pytest.mark.story10
@pytest.mark.parametrize('keyword', [None, 42, 'x' * 201])
def test_search_boundary_validates_before_querying(app, monkeypatch, keyword):
    lookup = Mock(side_effect=AssertionError('Invalid search reached the controller'))
    monkeypatch.setattr(SearchUserAccountController, 'searchUserAccounts', lookup)
    with app.test_request_context('/accounts/search'):
        page = SearchUserAccountPage()
        assert page.onSearch(keyword) is None
        assert 'Search text' in page.rendered_page
    lookup.assert_not_called()


@pytest.mark.parametrize('action', ['create', 'view', 'update', 'suspend', 'search'])
def test_boundary_event_methods_return_void(app, saved_account, action):
    account_id, profile_id = saved_account
    with app.test_request_context('/accounts'):
        if action == 'create':
            page = CreateUserAccountPage()
            assert page.clickCreate('second', 'Second User', 'second@example.com', '+65 6123 4567', profile_id) is None
        elif action == 'view':
            page = ViewUserAccountPage()
            assert page.onView(account_id) is None
        elif action == 'update':
            page = UpdateUserAccountPage()
            assert page.onUpdate(account_id, 'Updated User', 'updated@example.com', profile_id) is None
        elif action == 'suspend':
            page = SuspendUserAccountPage()
            assert page.onSuspend(account_id) is None
        else:
            page = SearchUserAccountPage()
            assert page.onSearch('customer') is None
        assert page.rendered_page
        if action in ('create', 'update', 'suspend'):
            assert page.rendered_page.status_code == 302
        else:
            assert 'customer1' in page.rendered_page


@pytest.mark.story6
def test_create_html_errors_stop_at_boundary_and_keep_escaped_values(app, client, submit, seed, monkeypatch):
    profile_id = seed('Customer')
    received = []
    create = UserAccount.createUserAccount

    def observe(self, username, fullName, email, phoneNumber, profileId, **kwargs):
        received.append((username, fullName, email, profileId))
        return create(self, username, fullName, email, phoneNumber, profileId, **kwargs)

    monkeypatch.setattr(UserAccount, 'createUserAccount', observe)
    full_name = 'Name <script>alert(1)</script>'
    response = submit('/accounts/create', dict(username='customer1', full_name=full_name,
        email='invalid-email', phone_number='+65 6123 4567', profile_id=profile_id))
    assert response.status_code == 400
    assert received == []
    html = response.get_data(as_text=True)
    controls = Controls(html)
    assert controls.value('full_name') == full_name
    assert controls.value('email') == 'invalid-email'
    assert any(item.get('value') == str(profile_id) and 'selected' in item for item in controls.items)
    assert '<script>alert(1)</script>' not in html
    assert 'Enter a valid email address.' in html
    with app.app_context():
        assert UserAccount.searchUserAccounts() == []


@pytest.mark.story8
def test_update_html_loads_saved_values_and_keeps_failed_edits(app, client, saved_account, submit, seed):
    account_id, profile_id = saved_account
    designer_id = seed('Designer')
    response = client.get(f'/accounts/{account_id}/update')
    assert response.status_code == 200
    controls = Controls(response.get_data(as_text=True))
    assert controls.value('full_name') == 'Customer One'
    assert controls.value('email') == 'customer@example.com'
    assert any(item.get('value') == str(profile_id) and 'selected' in item for item in controls.items)
    response = submit(f'/accounts/{account_id}/update', dict(full_name='Changed <name>',
        email='invalid-email', profile_id=designer_id))
    assert response.status_code == 400
    controls = Controls(response.get_data(as_text=True))
    assert controls.value('full_name') == 'Changed <name>'
    assert any(item.get('value') == str(designer_id) and 'selected' in item for item in controls.items)
    with app.app_context():
        account = UserAccount.getUserAccount(account_id)
        assert account.full_name == 'Customer One' and account.profile_id == profile_id
