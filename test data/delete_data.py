"""Empty the application tables except one admin and the four portal profiles.

From the project folder:
    .venv/bin/python "test data/delete_data.py"
    .venv/bin/python "test data/delete_data.py" --admin YOUR_ADMIN_USERNAME

The script uses the website's database configuration. It asks you to type
DELETE before changing data; --yes skips that prompt for an intentional run.
No tables, passwords, preserved IDs, or profile details are changed.
"""
import argparse
import sys
from pathlib import Path

# Make app.py importable when running this file from the test data folder.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import MetaData, func, select
from sqlalchemy.exc import SQLAlchemyError

# app.py loads the same database configuration as the website.
from app import create_app
# infrastructure/database.py provides the shared database engine.
from infrastructure.database import db


PORTAL_PROFILES = {
    'User Admin': ('user admin',),
    'Customer': ('customer',),
    'Interior Designer': ('interior designer',),
    'Platform Management': ('platform management', 'platform manager'),
}


def delete_data(admin_username=None, *, confirm=True):
    """Delete other rows in one transaction, preserving a chosen admin and four roles."""
    with db.engine.begin() as connection:
        # Reflect existing tables so unused legacy login/session tables are cleared too.
        metadata = MetaData()
        metadata.reflect(bind=connection)
        if 'user_account' not in metadata.tables or 'user_profile' not in metadata.tables:
            raise RuntimeError('Account/profile tables are missing. Run flask --app app upgrade-db first.')
        accounts = metadata.tables['user_account']
        profiles = metadata.tables['user_profile']
        saved_profiles = connection.execute(select(profiles)).mappings().all()
        by_name = {row['name'].casefold(): row for row in saved_profiles}
        kept_profiles = []
        for label, aliases in PORTAL_PROFILES.items():
            profile = next((by_name[name] for name in aliases if name in by_name), None)
            if profile is None:
                raise RuntimeError(f'Required portal profile is missing: {label}. No data was deleted.')
            kept_profiles.append(profile)

        admins = connection.execute(select(accounts).where(
            accounts.c.profile_id == kept_profiles[0]['profile_id']).order_by(accounts.c.username)).mappings().all()
        if admin_username:
            admin = next((row for row in admins if row['username'].casefold() == admin_username.casefold()), None)
            if admin is None:
                raise RuntimeError('The selected username must belong to the User Admin profile. No data was deleted.')
        else:
            admin = next((row for row in admins if row['username'].casefold() == 'admin'), None)
            if admin is None:
                # The generator names its demo administrators admin01 through admin10.
                originals = [row for row in admins if not (
                    row['username'].casefold() in {f'admin{i:02d}' for i in range(1, 11)}
                    and row['email'].casefold() == row['username'].casefold() + '@nestora-demo.sg')]
                if len(originals) == 1:
                    admin = originals[0]
                elif len(admins) == 1:
                    admin = admins[0]
            if admin is None:
                choices = ', '.join(row['username'] for row in admins) or '(none)'
                raise RuntimeError('Choose the admin to keep with --admin USERNAME. '
                                   f'User Admin accounts: {choices}. No data was deleted.')

        kept_profile_ids = [row['profile_id'] for row in kept_profiles]
        print(f"Keep admin: {admin['username']} (ID {admin['account_id']})", flush=True)
        print('Keep profiles: ' + ', '.join(row['name'] for row in kept_profiles), flush=True)
        print('All other account, profile, company, project, category, shortlist, report, '
              'activity and legacy table rows will be deleted.', flush=True)
        if confirm:
            try:
                answer = input('Type DELETE to continue: ')
            except EOFError:
                answer = ''
            if answer != 'DELETE':
                print('Cancelled. No data was deleted.')
                return None

        # Older SQLite installations can use a trigger instead of a category FK.
        # Add the dependency to this local table map so projects are deleted first.
        if 'interior_design_project' in metadata.tables and 'category' in metadata.tables:
            metadata.tables['interior_design_project'].add_is_dependent_on(metadata.tables['category'])

        deleted = {}
        for table in reversed(metadata.sorted_tables):
            statement = table.delete()
            if table.name == 'user_account':
                statement = statement.where(table.c.account_id != admin['account_id'])
            elif table.name == 'user_profile':
                statement = statement.where(table.c.profile_id.not_in(kept_profile_ids))
            result = connection.execute(statement)
            deleted[table.name] = result.rowcount

        # Any failed preservation check rolls back the entire cleanup.
        for table in metadata.tables.values():
            expected = 1 if table.name == 'user_account' else 4 if table.name == 'user_profile' else 0
            remaining = connection.scalar(select(func.count()).select_from(table))
            if remaining != expected:
                raise RuntimeError(f'Unexpected remaining rows in {table.name}; cleanup was rolled back.')

        result = {'admin': admin['username'], 'admin_id': admin['account_id'],
                  'profiles': [row['name'] for row in kept_profiles], 'deleted': deleted}
    print('Cleanup complete: one admin account and four portal profiles remain.', flush=True)
    print('The preserved admin keeps its existing password and account details.', flush=True)
    return result


def main():
    """Read the optional admin choice and run cleanup against the configured database."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--admin', help='Username of the User Admin account to preserve.')
    parser.add_argument('--yes', action='store_true', help='Skip the DELETE confirmation prompt.')
    args = parser.parse_args()
    try:
        with create_app().app_context():
            delete_data(args.admin, confirm=not args.yes)
    except (RuntimeError, SQLAlchemyError) as error:
        print(f'Cleanup failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
