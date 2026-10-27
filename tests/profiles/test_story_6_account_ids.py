"""Profile-ID prefixes and one persisted account sequence across all roles."""
from concurrent.futures import ThreadPoolExecutor

import pytest

from entity.user_account import AccountIdCounter, UserAccount
from entity.user_profile import UserProfile
from infrastructure.database import db

pytestmark = pytest.mark.story6


def test_TC70_account_sequence_is_shared_across_profiles(app, create_account):
    with app.app_context():
        assert UserAccount.getByUsername('admin').account_id == '101'
    assert create_account('customer1', 'Customer') == '202'
    assert create_account('designer1', 'Interior Designer') == '303'
    assert create_account('customer2', 'Customer') == '204'
    assert create_account('anotheradmin', 'User Admin') == '105'


def test_TC71_prefix_uses_actual_multi_digit_profile_id(app, admin_client, create_account):
    with app.app_context():
        db.session.add(UserProfile(profile_id=12, name='Custom role', description='Custom role',
                                   permissions=[], status='Active'))
        db.session.commit()
    assert create_account('customuser', 'Custom role') == '1202'


def test_TC72_existing_accounts_and_legacy_counters_are_preserved(app, seed):
    admin_profile_id = seed('User Admin')
    customer_profile_id = seed('Customer')
    with app.app_context():
        legacy = UserAccount(account_id='UA101', username='legacy_admin', full_name='Existing Admin',
            email='legacy@example.com', phone_number='+65 6123 4567', profile_id=admin_profile_id, status='Active')
        legacy.set_password('Fixture-Account-Password-123')
        db.session.add_all([legacy, AccountIdCounter(prefix='UA', next_number=102)])
        db.session.commit()
        assert UserAccount.createUserAccount('new_customer', 'New Customer',
            'new@example.com', '+65 6123 4567', customer_profile_id)
        assert UserAccount.getByUsername('new_customer').account_id == '202'
        assert UserAccount.getByUsername('legacy_admin').account_id == 'UA101'
        assert db.session.get(AccountIdCounter, 'UA').next_number == 102


def test_TC73_existing_numeric_id_collision_is_skipped(app, admin_client, create_account):
    with app.app_context():
        db.session.add(UserProfile(profile_id=11, name='Imported role', description='Imported',
                                   permissions=[], status='Active'))
        db.session.flush()
        db.session.add(UserAccount(account_id='1101', username='imported', full_name='Imported Account',
            email='imported@example.com', phone_number='+65 6123 4567', profile_id=11, status='Active',
            password_hash=UserAccount.getByUsername('admin').password_hash))
        db.session.get(AccountIdCounter, '*').next_number = 101
        db.session.commit()
    # Profile 1 + number 101 would duplicate profile 11 + number 01.
    assert create_account('anotheradmin', 'User Admin') == '1102'
    with app.app_context():
        assert UserAccount.getByUsername('imported').account_id == '1101'
        assert db.session.get(AccountIdCounter, '*').next_number == 103


def test_TC74_account_numbers_can_grow_beyond_two_digits(app, admin_client, create_account):
    with app.app_context():
        db.session.get(AccountIdCounter, '*').next_number = 100
        db.session.commit()
    assert create_account() == '2100'


def test_TC75_failed_creation_rolls_back_account_number(app, admin_client, create_account):
    with app.app_context():
        customer_profile_id = UserProfile.getProfile('Customer').profile_id
        assert not UserAccount.createUserAccount('would_fail', 'Duplicate Email',
            'admin@example.com', '+65 6123 4567', customer_profile_id)
    assert create_account() == '202'


def test_TC76_concurrent_creations_allocate_distinct_shared_numbers(app, admin_client):
    with app.app_context():
        profile_ids = [UserProfile.getProfile(name).profile_id for name in ('Customer', 'Interior Designer')]

    def create(index):
        with app.app_context():
            username = f'concurrent{index}'
            profile_id = profile_ids[index % len(profile_ids)]
            assert UserAccount.createUserAccount(username, username,
                f'{username}@example.com', '+65 6123 4567', profile_id)
            return profile_id, UserAccount.getByUsername(username).account_id

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(create, range(8)))
    assert len({account_id for _, account_id in results}) == 8
    assert sorted(int(account_id[len(str(profile_id)):]) for profile_id, account_id in results) == list(range(2, 10))
