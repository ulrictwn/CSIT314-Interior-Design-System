# Test data scripts

Run these commands from the project folder using the project's virtual environment. These scripts use the same database configuration as the website in `app.py`/`.env`.

Create the sample data:

```bash
.venv/bin/python "test data/create_data.py"
```

Clear the database while keeping your admin and four portal profiles:

```bash
.venv/bin/python "test data/delete_data.py" --admin admin
```

Replace `admin` with your admin's username. The cleanup shows which account/profiles it will keep and asks you to type `DELETE`. Add `--yes` only when you intend to skip that prompt.

On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.

## List saved records one per line

Save a snapshot of the actual website database:

```bash
.venv/bin/python "test data/list_data.py" --output "test data/exports/current_data.txt"
```

Open `test data/exports/current_data.txt` in VS Code. Each section shows its total saved count and one JSON record per line. Listings include IDs, names, descriptions, statuses, profile/category assignments, designer/customer usernames, project view/shortlist counts, dates, and the stored report totals. Display IDs match the website: `IDP1`, `CAT1` and `RPT-D-1`. All timestamps are labelled in Singapore time.

To inspect a single group in the terminal:

```bash
.venv/bin/python "test data/list_data.py" --table accounts
.venv/bin/python "test data/list_data.py" --table projects --limit 10
```

Available groups: `profiles`, `accounts`, `companies`, `categories`, `projects`, `shortlists`, `reports`, and `activity`; the default is `all`. Counts always show full totals even when `--limit` previews fewer rows. Empty sections are shown explicitly. The header records the export time and whether the `customer001` demo marker exists.

For direct backend comparisons, the listing groups correspond to these SQL tables:

| Listing group | SQL table |
| --- | --- |
| profiles | user_profile |
| accounts | user_account |
| companies | company_profile |
| categories | category |
| projects | interior_design_project |
| shortlists | shortlist |
| reports | report |
| activity | activity_event |

This is a read-only listing of records already stored in the database. It does not create demo data, migrate tables, increment project views, or regenerate reports. Generate the sample data first if it is missing, and refresh the listing after website changes. Password hashes/session secrets are omitted. Generated exports are ignored by Git. A failed export preserves the previous text snapshot.

## Created data

The creator retains the dataset from the original `seed_data.py`:

| Data | Sample count |
| --- | ---: |
| User profiles | 100: four portal profiles and 96 additional roles |
| User accounts | 220: 100 Customers, 100 Interior Designers, 10 Platform Managers, 10 User Admins |
| Company profiles | 100 |
| IDP categories | 100 |
| Projects | 300: 150 New and 150 Past |
| Shortlists | 300 |
| Reports | 100: 70 daily, 20 weekly, 10 monthly |
| Additional activity | 3,000 login events and 4,000 project-view events |

Existing portal profiles are reused. An existing admin adds to the account total unless its username is one of the demo admin names being reused. New sample accounts use the password `password`; existing admins keep their original details and password.

The creator uses entity methods for business records, records all 300 shortlist saves, and backdates only activity it creates. Historical dates are synthetic demo data. Data creation runs in one outer transaction, so an error rolls back the generated rows despite the entity methods' commits. Missing tables/compatible upgrades are prepared before seeding. An existing `customer001` prevents another seed run; clear the data before generating it again.

The original root command `.venv/bin/python seed_data.py` remains a compatibility launcher.

## Kept after cleanup

Exactly one selected User Admin account and these four saved profiles remain:

- User Admin
- Customer
- Interior Designer
- Platform Management (or the existing Platform Manager profile)

Their IDs, passwords, status, descriptions and permission values are preserved. Every other application row is deleted, including extra/demo admins, extra profiles, companies, projects, categories, shortlists, reports, activity, account counters and legacy login/session rows. Tables and database definitions remain available for another seed run. Account numbering is reinitialized by the entity when the next account is created.

If `--admin` is omitted, cleanup prefers username `admin`, then a unique existing non-demo admin, then the only User Admin account if there is just one. Ambiguous selection or a missing required profile stops cleanup before deletion. Cleanup is a single transaction: any failure rolls back its deletions.

These scripts create and clear real demonstration data. Automated pytest tests continue using their separate disposable databases.

## Verification

The complete create → cleanup → create cycle passed on disposable SQLite and PostgreSQL databases. Checks covered the full dataset counts, 300 shortlist-save events, preserved admin/profile rows and passwords, existing activity history, retained demo-admin reuse, the Platform Manager profile alias, legacy login/session tables, cancellation, invalid/ambiguous admin choices, and forced failures rolling back both seeding and deletion. These checks did not run against the website database.

The listing was also verified on disposable SQLite and PostgreSQL databases: all eight groups, related names/counts, website display IDs, multiline JSON fields, legacy report snapshots, Singapore timestamps, empty sections and preview limits passed. Saved database fingerprints were unchanged, and a failed export preserved the previous output file.
