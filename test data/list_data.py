"""List actual saved records, one per line, for comparison with the website.

From the project folder:
    .venv/bin/python "test data/list_data.py"
    .venv/bin/python "test data/list_data.py" --table accounts
    .venv/bin/python "test data/list_data.py" --output "test data/exports/current_data.txt"

Reads the configured website database without creating, updating or deleting
records. Password hashes and session secrets are not included. Dates/times are
labelled in Singapore time; displayed CAT/IDP/report IDs match the website.
"""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from zoneinfo import ZoneInfo

# The project root contains app.py and the entity packages.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

# app.py supplies the website's database configuration.
from app import create_app
# infrastructure/database.py supplies the shared database engine.
from infrastructure.database import db
# infrastructure/permissions.py contains the permission labels shown in forms.
from infrastructure.permissions import PERMISSION_OPTIONS
# entity/models.py registers and exports the project's saved-data models.
from entity.models import (UserProfile, UserAccount, CompanyProfile, Category,
                           InteriorDesignProject, Shortlist, Report, ActivityEvent)

SINGAPORE = ZoneInfo('Asia/Singapore')
TABLES = {
    'profiles': ('USER PROFILES', UserProfile),
    'accounts': ('USER ACCOUNTS', UserAccount),
    'companies': ('COMPANY PROFILES', CompanyProfile),
    'categories': ('IDP CATEGORIES', Category),
    'projects': ('INTERIOR DESIGN PROJECTS', InteriorDesignProject),
    'shortlists': ('CUSTOMER SHORTLISTS', Shortlist),
    'reports': ('SAVED REPORTS', Report),
    'activity': ('ACTIVITY EVENTS', ActivityEvent),
}


def listing_queries():
    """Select comparison fields and related names without calling mutating entity methods."""
    category_counts = select(InteriorDesignProject.category_id,
        func.count().label('projectCount')).group_by(InteriorDesignProject.category_id).subquery()
    shortlist_counts = select(Shortlist.project_id,
        func.count().label('shortlistCount')).group_by(Shortlist.project_id).subquery()
    return {
        'profiles': select(
            UserProfile.profile_id.label('profileId'), UserProfile.name.label('profileName'),
            UserProfile.description, UserProfile.status, UserProfile.permissions
        ).order_by(UserProfile.profile_id),
        'accounts': select(
            UserAccount.account_id.label('accountId'), UserAccount.username,
            UserAccount.full_name.label('fullName'), UserAccount.email,
            UserAccount.phone_number.label('phoneNumber'), UserAccount.profile_id.label('profileId'),
            UserProfile.name.label('profileName'), UserAccount.status,
            UserProfile.status.label('profileStatus'), UserAccount.created_at.label('createdAtSGT')
        ).select_from(UserAccount).outerjoin(UserProfile,
            UserProfile.profile_id == UserAccount.profile_id).order_by(UserAccount.account_id),
        'companies': select(
            CompanyProfile.account_id.label('accountId'), UserAccount.username.label('designerUsername'),
            CompanyProfile.company_name.label('companyName'),
            CompanyProfile.company_contact.label('companyContact'),
            CompanyProfile.company_address.label('companyAddress'),
            CompanyProfile.company_email.label('companyEmail'),
            CompanyProfile.company_registration_number.label('companyRegistrationNumber')
        ).select_from(CompanyProfile).outerjoin(UserAccount,
            UserAccount.account_id == CompanyProfile.account_id).order_by(CompanyProfile.account_id),
        'categories': select(
            Category.category_id.label('categoryId'), Category.category_name.label('categoryName'),
            Category.description, func.coalesce(category_counts.c.projectCount, 0).label('projectCount')
        ).select_from(Category).outerjoin(category_counts,
            category_counts.c.category_id == Category.category_id).order_by(Category.category_id),
        'projects': select(
            InteriorDesignProject.project_id.label('projectId'),
            InteriorDesignProject.project_name.label('projectName'),
            InteriorDesignProject.account_id.label('designerAccountId'),
            UserAccount.username.label('designerUsername'), UserAccount.full_name.label('designerName'),
            CompanyProfile.company_name.label('companyName'),
            InteriorDesignProject.category_id.label('categoryId'),
            Category.category_name.label('categoryName'),
            InteriorDesignProject.property_type.label('propertyType'), InteriorDesignProject.area,
            InteriorDesignProject.renovation_cost.label('renovationCost'),
            InteriorDesignProject.description, InteriorDesignProject.project_status.label('status'),
            InteriorDesignProject.view_count.label('viewCount'),
            func.coalesce(shortlist_counts.c.shortlistCount, 0).label('shortlistCount')
        ).select_from(InteriorDesignProject).outerjoin(UserAccount,
            UserAccount.account_id == InteriorDesignProject.account_id).outerjoin(CompanyProfile,
            CompanyProfile.account_id == InteriorDesignProject.account_id).outerjoin(Category,
            Category.category_id == InteriorDesignProject.category_id).outerjoin(shortlist_counts,
            shortlist_counts.c.project_id == InteriorDesignProject.project_id)
            .order_by(InteriorDesignProject.project_id),
        'shortlists': select(
            Shortlist.account_id.label('customerAccountId'), UserAccount.username.label('customerUsername'),
            Shortlist.project_id.label('projectId'), InteriorDesignProject.project_name.label('projectName'),
            InteriorDesignProject.project_status.label('status'),
            InteriorDesignProject.account_id.label('designerAccountId'),
            Category.category_name.label('categoryName'), Shortlist.saved_at.label('savedAtSGT')
        ).select_from(Shortlist).outerjoin(UserAccount,
            UserAccount.account_id == Shortlist.account_id).outerjoin(InteriorDesignProject,
            InteriorDesignProject.project_id == Shortlist.project_id).outerjoin(Category,
            Category.category_id == InteriorDesignProject.category_id)
            .order_by(Shortlist.account_id, Shortlist.project_id),
        'reports': select(
            Report.report_id.label('reportId'), Report.report_type.label('type'),
            Report.start_date.label('startDate'), Report.end_date.label('endDate'),
            Report.generated_at.label('generatedAtSGT'), Report.account_id.label('generatedByAccountId'),
            UserAccount.username.label('generatedByUsername'), Report.totals, Report.rows
        ).select_from(Report).outerjoin(UserAccount,
            UserAccount.account_id == Report.account_id).order_by(Report.report_id),
        'activity': select(
            ActivityEvent.event_id.label('eventId'), ActivityEvent.kind,
            ActivityEvent.target_id.label('targetId'), ActivityEvent.category_id.label('categoryId'),
            ActivityEvent.category_name.label('categoryName'), ActivityEvent.occurred_at.label('occurredAtSGT')
        ).order_by(ActivityEvent.event_id),
    }


def format_record(table, row):
    """Add the website's display IDs and permission labels to a saved record."""
    values = dict(row)
    if 'projectId' in values:
        values['projectDisplayId'] = f"IDP{values['projectId']}"
    if values.get('categoryId') is not None:
        values['categoryDisplayId'] = f"CAT{values['categoryId']}"
    if table == 'profiles':
        values['permissionLabels'] = [PERMISSION_OPTIONS.get(code, code)
                                     for code in values['permissions'] or []]
    if table == 'reports':
        values['reportDisplayId'] = f"RPT-{values['type'][0].upper()}-{values['reportId']}"
    return values


def json_value(value):
    """Serialize dates and convert saved UTC timestamps to labelled Singapore time."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(SINGAPORE).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f'Unsupported listing value: {type(value).__name__}')


def write_listing(stream, table='all', limit=None):
    """Read one database snapshot and write one JSON record per physical line."""
    selected = list(TABLES) if table == 'all' else [table]
    queries = listing_queries()
    with db.engine.connect() as connection:
        if connection.dialect.name == 'postgresql':
            connection = connection.execution_options(isolation_level='REPEATABLE READ')
        with connection.begin():
            if connection.dialect.name == 'postgresql':
                connection.exec_driver_sql('SET TRANSACTION READ ONLY')
            elif connection.dialect.name == 'sqlite':
                connection.exec_driver_sql('BEGIN')
            counts = {name: connection.scalar(select(func.count()).select_from(TABLES[name][1]))
                      for name in selected}
            print('NESTORA — SAVED DATABASE RECORDS', file=stream)
            print('Exported: ' + datetime.now(SINGAPORE).isoformat(timespec='seconds'), file=stream)
            print('Database engine: ' + connection.dialect.name, file=stream)
            print('All timestamps use Singapore time (+08:00). Each JSON line is one saved record.', file=stream)
            print('Counts: ' + ', '.join(f'{name}={count}' for name, count in counts.items()), file=stream)
            if counts.get('accounts') is not None:
                sample_exists = connection.scalar(select(UserAccount.account_id).where(
                    func.lower(UserAccount.username) == 'customer001').limit(1)) is not None
                print('Demo seed marker customer001: ' + ('present' if sample_exists else 'not present'), file=stream)
            if limit is not None:
                print(f'Displaying at most {limit} records per section; counts above are full table totals.', file=stream)
            for name in selected:
                query = queries[name].limit(limit) if limit is not None else queries[name]
                print(f'\n=== {TABLES[name][0]} ({counts[name]} saved records) ===', file=stream)
                shown = 0
                for row in connection.execute(query).mappings():
                    print(json.dumps(format_record(name, row), ensure_ascii=False, default=json_value), file=stream)
                    shown += 1
                if shown == 0:
                    print('(No saved records.)', file=stream)
                elif shown < counts[name]:
                    print(f'({shown} of {counts[name]} records displayed.)', file=stream)
    return counts



def save_listing(output, table='all', limit=None):
    """Replace the text snapshot only after every selected record was read successfully."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile('w', encoding='utf-8', dir=output.parent,
                                prefix='.' + output.name + '.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            counts = write_listing(stream, table, limit)
        temporary.replace(output)
        return counts
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def positive_limit(value):
    """Require a positive record limit when a preview is requested."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('--limit must be at least 1.')
    return number


def main():
    """List records in the terminal or save the same listing to the requested text file."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--table', choices=['all', *TABLES], default='all', help='Table group to list (default: all).')
    parser.add_argument('--limit', type=positive_limit, help='Preview at most this many records per section.')
    parser.add_argument('--output', type=Path, help='Save the listing to a text file instead of printing all records.')
    args = parser.parse_args()
    try:
        with create_app().app_context():
            if args.output:
                counts = save_listing(args.output, args.table, args.limit)
                print('Saved listing: ' + str(args.output))
                print('Saved records: ' + ', '.join(f'{name}={count}' for name, count in counts.items()))
            else:
                write_listing(sys.stdout, args.table, args.limit)
    except (OSError, SQLAlchemyError) as error:
        parser.exit(1, f'Could not list records: {error}\n')


if __name__ == '__main__':
    main()
