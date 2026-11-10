"""Create the complete classroom demo dataset in the website's configured database.

Run from the project folder:
    .venv/bin/python "test data/create_data.py"

Creates 100 profiles, 220 demo accounts, 100 companies, 100 categories,
300 projects (150 New and 150 Past), 300 shortlists and 100 saved reports
(70 daily, 20 weekly and 10 monthly), plus dated synthetic activity.

New demo accounts use the password "password". Existing User Admin accounts
are preserved; an existing admin01..admin10 is reused without changing it.
The displayed totals include any other existing administrator account.

All business records use the real entity operations. New activity is dated
within the last 300 days; existing activity timestamps are preserved. A failed
seed rolls back every new data record, including entity-method commits. Table
creation/upgrades are applied before that data transaction.
"""
import argparse
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker

# The project root contains app.py and the BCE packages.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# app.py supplies the website's database configuration and registered models.
from app import create_app
# infrastructure/database.py provides the shared database/session used by entities.
from infrastructure.database import db
# infrastructure/migrations.py creates/upgrades tables without resetting data.
from infrastructure.migrations import upgrade_database
# infrastructure/permissions.py defines the four portal profiles and permission labels.
from infrastructure.permissions import DEFAULT_PROFILES, PERMISSION_OPTIONS
# These entity files contain the real business validation and persistence operations.
from entity.profile.user_profile import UserProfile
from entity.accounts.user_account import UserAccount
from entity.company.company_profile import CompanyProfile
from entity.categories.category import Category
from entity.projects.interior_design_project import InteriorDesignProject
from entity.shortlist.shortlist import Shortlist
from entity.reports.activity_event import ActivityEvent
from entity.reports.report import Report

PASSWORD = 'password'
DAYS = 300
NOW = datetime.now(timezone.utc)
RANDOM = random.Random(314)
SINGAPORE = ZoneInfo('Asia/Singapore')

FIRST = ['Aisha', 'Benjamin', 'Chloe', 'Daniel', 'Elaine', 'Farhan', 'Grace', 'Hafiz', 'Isabel', 'Jun Wei',
         'Kavitha', 'Liam', 'Mei Ling', 'Nur', 'Oliver', 'Priya', 'Qi Hui', 'Rajesh', 'Siti', 'Timothy',
         'Umairah', 'Vincent', 'Wei Jie', 'Xin Yi', 'Yusof', 'Zara', 'Arjun', 'Bee Lian', 'Cheng', 'Divya']
LAST = ['Tan', 'Lim', 'Lee', 'Ng', 'Wong', 'Goh', 'Chua', 'Ong', 'Koh', 'Teo', 'Rahman', 'Ismail',
        'Kumar', 'Pillai', 'Nair', 'Fernandez', 'Chan', 'Yeo', 'Sim', 'Ho']
AREAS = ['Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Batok', 'Bukit Timah', 'Clementi', 'Hougang', 'Jurong East',
         'Jurong West', 'Kallang', 'Marine Parade', 'Pasir Ris', 'Punggol', 'Queenstown', 'Sengkang',
         'Serangoon', 'Tampines', 'Toa Payoh', 'Woodlands', 'Yishun', 'Novena', 'Tanglin', 'Bukit Panjang']
PROPERTY_TYPES = ['HDB 3-Room', 'HDB 4-Room', 'HDB 5-Room', 'HDB Executive', 'Condominium',
                  'Landed Terrace', 'Semi-Detached', 'Bungalow', 'Commercial Office', 'Retail Shop']
STYLES = ['Scandinavian', 'Japandi', 'Industrial', 'Minimalist', 'Modern Luxe', 'Contemporary',
          'Mid-Century Modern', 'Bohemian', 'Coastal', 'Rustic', 'Peranakan', 'Tropical', 'Art Deco',
          'Farmhouse', 'Vintage', 'Wabi-Sabi', 'Eclectic', 'Classic', 'Transitional', 'Urban']
ROOMS = ['Living Room', 'Kitchen', 'Bedroom', 'Bathroom', 'Whole Home']
DEPARTMENTS = ['Sales', 'Marketing', 'Finance', 'Customer Support', 'Content', 'Quality Assurance',
               'Operations', 'Partnerships', 'Design Review', 'Data Analytics', 'Compliance', 'Training']
LEVELS = ['Intern', 'Assistant', 'Officer', 'Analyst', 'Lead', 'Manager', 'Senior Manager', 'Director']
STUDIO_WORDS = ['Atelier', 'Studio', 'Design House', 'Interiors', 'Living', 'Spaces', 'Concepts', 'Works']
STUDIO_NAMES = ['Oak', 'Linen', 'Harbour', 'Lumen', 'Kanso', 'Verde', 'Stone', 'Willow', 'Ember', 'Sora',
                'Marble', 'Indigo', 'Cedar', 'Haven', 'Nook', 'Arc', 'Bloom', 'Tide', 'Fern', 'Slate']



def check(ok, entity, what):
    """Stop the transaction if an entity rejects a demo record."""
    if not ok:
        raise RuntimeError(f'Could not create {what}: {entity.error_message} {entity.field_errors}')


def random_time(days=DAYS):
    """Choose a UTC timestamp within the requested demo-history interval."""
    return NOW - timedelta(days=RANDOM.uniform(0, days))


def person(i):
    """Generate a repeatable display name for a sample account."""
    return f'{FIRST[i % len(FIRST)]} {LAST[(i * 7) % len(LAST)]}'


def phone(i):
    """Generate a valid sample Singapore telephone number."""
    return f'+65 {RANDOM.choice("689")}{1000000 + i * 7919 % 8999999:07d}'


def profile_id(name, description):
    """Reuse a portal role or create it through entity/profile/user_profile.py."""
    profile = UserProfile.getProfile(name)
    if profile is None and name == 'Platform Management':
        profile = UserProfile.getProfile('Platform Manager')
    if profile is None:
        profile = UserProfile()
        check(profile.createUserProfile(name, description, 'Active', DEFAULT_PROFILES[name]), profile, name)
    return profile.profile_id


def backdate_activity(kind, target_id):
    """Date the event just created for a new seed record, leaving older events alone."""
    event = db.session.scalar(db.select(ActivityEvent).where(
        ActivityEvent.kind == kind, ActivityEvent.target_id == str(target_id))
        .order_by(ActivityEvent.event_id.desc()).limit(1))
    if event is None:
        raise RuntimeError(f'The entity did not record {kind} for {target_id}.')
    event.occurred_at = random_time()
    return event.occurred_at


def _seed_records():
    """Build the original demo dataset inside seed()'s outer transaction."""
    if UserAccount.getByUsername('customer001'):
        raise RuntimeError('Seed data already exists (customer001 found). Run delete_data.py first.')

    print('Creating 100 user profiles...', flush=True)
    roles = {
        'User Admin': profile_id('User Admin', 'Manages user accounts and user profiles.'),
        'Customer': profile_id('Customer', 'Homeowners who search and shortlist interior design projects.'),
        'Interior Designer': profile_id('Interior Designer', 'Designers who manage their company and projects.'),
        'Platform Management': profile_id('Platform Management', 'Manages IDP categories and reports.'),
    }
    extra = [f'{d} {lvl}' for d in DEPARTMENTS for lvl in LEVELS][:100 - len(roles)]
    for n, name in enumerate(extra):
        if UserProfile.getProfile(name):
            continue
        perms = RANDOM.sample(sorted(PERMISSION_OPTIONS), k=RANDOM.randint(1, 5))
        status = 'Suspended' if n % 12 == 11 else 'Active'
        entity = UserProfile()
        check(entity.createUserProfile(name, f'{name} role for the {name.split()[0]} team.', status, perms),
              entity, name)

    print('Creating 220 demo user accounts...', flush=True)

    def make_accounts(prefix, count, role, width):
        """Create sample accounts, preserving any retained admin01..admin10 unchanged."""
        ids = []
        for i in range(1, count + 1):
            username = f'{prefix}{i:0{width}d}'
            existing = UserAccount.getByUsername(username)
            if prefix == 'admin' and existing is not None and existing.profile_id == roles['User Admin']:
                ids.append(existing.account_id)
                continue
            full_name = person(i + len(prefix))
            entity = UserAccount()
            check(entity.createUserAccount(username, PASSWORD, full_name, f'{username}@nestora-demo.sg',
                                           phone(i + len(prefix) * 100), roles[role]), entity, username)
            entity.created_at = random_time()
            ids.append(entity.account_id)
        db.session.commit()
        return ids

    customers = make_accounts('customer', 100, 'Customer', 3)
    designers = make_accounts('designer', 100, 'Interior Designer', 3)
    managers = make_accounts('manager', 10, 'Platform Management', 2)
    make_accounts('admin', 10, 'User Admin', 2)

    print('Creating 100 company profiles...', flush=True)
    for i, account_id in enumerate(designers):
        name = f'{STUDIO_NAMES[i % 20]} {STUDIO_WORDS[(i // 20) % len(STUDIO_WORDS)]}'
        if i >= 40:
            name += f' {AREAS[i % len(AREAS)]}'
        entity = CompanyProfile()
        check(entity.createCompanyProfile(account_id, name, phone(5000 + i),
                                          f'{10 + i} {AREAS[i % len(AREAS)]} Avenue {i % 9 + 1}, Singapore',
                                          f'hello{i + 1:03d}@{STUDIO_NAMES[i % 20].lower()}-design.sg',
                                          f'UEN{201800000 + i * 37}K'), entity, name)

    print('Creating 100 IDP categories...', flush=True)
    category_ids = []
    for style in STYLES:
        for room in ROOMS:
            entity = Category()
            check(entity.createCategory(f'{style} {room}',
                                        f'{style} design ideas for the {room.lower()}.'), entity, style)
            category_ids.append(entity.category_id)
            backdate_activity('category_created', entity.category_id)

    print('Creating 300 interior design projects (150 new, 150 past)...', flush=True)
    project_ids = []
    for i, account_id in enumerate(designers):
        for kind in ('New', 'Past', 'New' if i % 2 == 0 else 'Past'):
            category_id = RANDOM.choice(category_ids)
            style_room = db.session.get(Category, category_id).category_name
            area = RANDOM.choice(AREAS)
            entity = InteriorDesignProject()
            name = f'{area} {style_room} {RANDOM.choice(["Refresh", "Makeover", "Renovation", "Revamp"])} {len(project_ids) + 1}'
            create = entity.createNewProject if kind == 'New' else entity.createPastProject
            check(create(account_id, name, category_id, RANDOM.choice(PROPERTY_TYPES), area,
                         round(RANDOM.uniform(15000, 250000), 2),
                         f"A {style_room.lower()} project in {area}, designed around the owner's daily routine."),
                  entity, name)
            entity.view_count = RANDOM.randint(0, 250)
            project_ids.append(entity.project_id)
            backdate_activity('project_' + kind.lower() + '_created', entity.project_id)
    db.session.commit()

    print('Creating 300 shortlist entries...', flush=True)
    for account_id in customers:
        for project_id in RANDOM.sample(project_ids, 3):
            entity = Shortlist()
            check(entity.saveShortlist(account_id, project_id), entity, 'shortlist')
            entity.saved_at = backdate_activity('shortlist_saved', project_id)
    db.session.commit()

    # Their earlier saved projects remain after these sample accounts are suspended.
    for account_id in customers[95:] + designers[97:]:
        entity = UserAccount()
        check(entity.suspendUserAccount(account_id), entity, 'account suspension')

    print('Adding platform activity over the last 300 days...', flush=True)
    for _ in range(3000):
        db.session.add(ActivityEvent(kind='login_success', target_id=RANDOM.choice(customers + designers),
                                     occurred_at=random_time()))
    for _ in range(4000):
        db.session.add(ActivityEvent(kind='project_viewed', target_id=str(RANDOM.choice(project_ids)),
                                     occurred_at=random_time()))
    db.session.commit()

    print('Generating 100 reports (70 daily, 20 weekly, 10 monthly)...', flush=True)
    today = NOW.astimezone(SINGAPORE).date()
    for d in range(1, 71):
        Report(account_id=managers[d % 10]).generateReport('daily', today - timedelta(days=d), None)
    for w in range(1, 21):
        start = today - timedelta(days=7 * w)
        Report(account_id=managers[w % 10]).generateReport('weekly', start, None)
    month_end = today.replace(day=1) - timedelta(days=1)
    for m in range(1, 11):
        month_start = month_end.replace(day=1)
        Report(account_id=managers[m % 10]).generateReport('monthly', month_start, month_end)
        month_end = month_start - timedelta(days=1)

    print('\nDataset totals (including any existing admin):')
    for label, model in [('User profiles', UserProfile), ('User accounts', UserAccount),
                         ('Company profiles', CompanyProfile), ('IDP categories', Category),
                         ('Interior design projects', InteriorDesignProject), ('Shortlist entries', Shortlist),
                         ('Reports', Report), ('Activity events', ActivityEvent)]:
        print(f'  {label:<26}{db.session.scalar(db.select(db.func.count()).select_from(model)):>6}')
    print('\nNew demo account passwords: password. Existing administrators keep their passwords.')
    print('Examples: customer001, designer001, manager01, admin01')


def seed():
    """Commit the full dataset together, or roll back every newly created record."""
    global NOW
    NOW = datetime.now(timezone.utc)
    RANDOM.seed(314)
    original_session = db.session
    original_session.remove()
    with db.engine.connect() as connection:
        with connection.begin():
            # Python's SQLite driver otherwise defers BEGIN until after SAVEPOINT.
            if connection.dialect.name == 'sqlite':
                connection.exec_driver_sql('BEGIN')
            seed_session = scoped_session(sessionmaker(bind=connection, join_transaction_mode='create_savepoint'))
            db.session = seed_session
            try:
                _seed_records()
                seed_session.commit()
            finally:
                seed_session.remove()
                db.session = original_session
    print('\nDemo data committed successfully.', flush=True)


def main():
    """Upgrade the configured database, then create the dataset through seed()."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()
    application = create_app()
    with application.app_context():
        upgrade_database()
        try:
            seed()
        except (RuntimeError, SQLAlchemyError) as error:
            raise SystemExit(f'{error}\nNo new seed data was committed.') from None


if __name__ == '__main__':
    main()
