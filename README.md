# Nestora — BCE stories 1–48

This application implements Stories 1–48: profile/account administration; staff/customer login; company profiles; design projects; customer discovery and shortlists; designer interest counts; categories; and platform activity reports. It contains the combined Flask application, PostgreSQL models, BCE classes, HTML templates, tests and GitHub Actions workflow. Sprint 4–5 screens follow the supplied customer and platform manager wireframes.

## Add this to your existing Codespace

1. Save your current work and use a working branch. Extract the ZIP outside your repository, then merge its files into the repository root (the folder containing `app.py`). Review the diff before committing, especially if teammates have changed the same files.
2. Keep your existing `.env`, `.postgres-data`, `.venv` and `.devcontainer` configuration. This package does not replace your working container setup or contain your database. Do not delete or reinitialize the database. Back up your existing database before changing its schema.
3. In the Codespace terminal, from the repository root, install the application and test dependencies:

   ```bash
   .venv/bin/python -m pip install -r requirements-dev.txt
   ```

   If this is a fresh Codespace without a virtual environment, first run `python -m venv .venv`. The new application dependency is `email-validator`; the requirements files install it automatically.

4. Keep the existing `.env` database credentials and `SECRET_KEY`. Sign in using the role associated with each portal. Login/logout use the configured key for a basic browser session.
5. With the database service running, apply the non-destructive upgrade:

   ```bash
   .venv/bin/python -m flask --app app upgrade-db
   ```

   This keeps existing records and creates missing account, company, and project tables. It supports the earlier four-column profile table and adds `status` when missing. An unfamiliar existing account schema stops the upgrade rather than deleting or converting records silently. Review a migration if that message appears.

6. Create the first administrator from the terminal:

   ```bash
   .venv/bin/python -m flask --app app bootstrap-admin
   ```

   Enter a username, email, phone number and a private password of 12–128 characters. Password input is hidden. This command creates any missing standard roles and explicitly activates the `User Admin` profile with the ten profile/account permissions. Other existing profiles keep their permissions. There is no default administrator password. Run it once per initial account, not every time you start the app.

7. Start the app:

   ```bash
   .venv/bin/python -m flask --app app run --host=0.0.0.0 --port=5000
   ```

   Open the forwarded **5000** port and sign in at `/login` for admins or `/designer/login` for designers. The login selector slides between Staff and Customer; Staff includes an Admin, Interior Designer, or Platform Manager role selector. Use the corresponding sidebar to manage accounts/profiles or company details/projects. You do not need to rebuild the container for Python, HTML or CSS edits. Rebuild only when its configuration or container-level dependencies change.

For a fresh Codespace, restore the correct database settings in the gitignored `.env`. `python scripts/setup_env.py` adds missing settings and preserves existing values; it cannot recover a previous database password.

Profile modules live in `boundary/profile/`, `control/profile/`, and `entity/profile/`; account modules use the matching `accounts/` packages. Boundaries strip ordinary text through `boundary/validation.py` and display results. Controllers relay calls through their entity object. Entities validate fields, formats, choices, duplicates, and saved data. See [the latest BCE review changes](docs/BCE_REVIEW_CHANGES.md). See [the BCE implementation map](docs/STORIES_1_12.md).

## What changes in the application

| Story | Feature | Main screen |
| --- | --- | --- |
| 1–5 | Create, view, update, suspend and search profiles | `/profiles` |
| 6 | Create account and assign an active profile | `/accounts/create` |
| 7 | View account details | `/accounts/<account_id>` |
| 8 | Update full name, email and assigned profile | `/accounts/<account_id>/update` |
| 9 | Confirm and suspend an account | `/accounts/<account_id>/suspend` |
| 10 | Search by account ID, username or full name | `/accounts/search` |
| 11 | Authenticate an active User Admin | `/login` |
| 12 | Clear the current browser login | Sidebar **Sign out** (POST `/logout`) |

Account creation collects username, full name, email, phone number and assigned profile. The Create User Account form has no Password or Confirm Password fields, and submissions do not need a password. The server generates the ID and an `Active` status. New account IDs combine the selected profile's actual database ID with a shared account number, padded to at least two digits: profile `1` + account `01` = `101`; profile `2` + account `02` = `202`; profile `3` + account `03` = `303`; another profile `2` account with number `04` = `204`. The number increases across all profiles, rather than restarting for each role. Profile names do not determine the prefix. Existing databases may have different profile IDs from these examples.

The account number grows beyond two digits after 99 (profile `2` + account `100` = `2100`). Because concatenated numbers can occasionally produce the same complete ID, occupied IDs are skipped. IDs remain fixed when a role is reassigned; the prefix records the profile at creation. Existing accounts keep their previous IDs. The shared counter is created automatically on first use, starting after the number of existing accounts, and is committed in the same transaction as the new account. See [ACCOUNT_ID_UPDATE.md](docs/ACCOUNT_ID_UPDATE.md) for how to apply this update.

New accounts created through the web form have no usable password. Before a newly created User Admin or Interior Designer can sign in, a trusted administrator sets a private password through `flask --app app reset-password --username <username>` in the server terminal. Bootstrap still creates the first administrator with a password. Existing stored passwords and login behavior are preserved; there is no default password or password-free sign-in. See [CREATE_ACCOUNT_UPDATE.md](docs/CREATE_ACCOUNT_UPDATE.md) for the files to copy and setup steps.

Update follows the report's editable fields: full name, email and assigned profile. Username, password, ID, status and stored phone number are not changed through this form. Suspension keeps the account record. Repeated suspension is rejected. Suspended accounts or profiles cannot complete a new login.

The profile Search screen retains the requested behavior: all profiles appear initially beneath the search bar, and a submitted query filters that table. An empty submitted profile query shows the existing validation message and all profiles. Account search has its own report requirement: blank or whitespace lists all accounts.

Story 11 demonstrates User Admin login. Stories 18–19 provide the separate Interior Designer login/logout flow. Pages require the matching active portal role, and permissions remain stored profile data. Profile suspension is still blocked when any account is assigned, including a suspended account.

Existing passwords stay hashed. Login checks entered credentials against saved account data and records only the account ID in a basic browser session. Logout clears that browser session. Admin-created accounts remain password-free. Basic login, portal-role, and designer ownership checks protect the pages. CSRF tokens, login rate limits, server-side session tokens, and final-admin protection remain outside this classroom scope.

Trusted terminal recovery commands:

```bash
.venv/bin/python -m flask --app app reset-password

```

The reset-password command configures the selected account for a login demonstration; it does not invalidate other browser sessions.

## Tests and GitHub Actions

```bash
.venv/bin/python scripts/run_profile_tests.py
```

Tests are organised into `tests/sprint_1/` through `tests/sprint_5/`, with one file per user story. Sprint 1 contains the Word document’s 22 checks (TC01–TC22); later sprints each have one test per story, for 65 tests total. The existing runner name is retained. Open `reports/test-results.html` for individual results or `reports/summary.md` for the sprint tables. See [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) and [TEST_CASES.md](docs/TEST_CASES.md).

The workflow `.github/workflows/profile-ci.yml` runs a SQLite/PostgreSQL matrix on push and pull requests. Its run Summary shows every result. Download `sprint-reports-SQLite` or `sprint-reports-PostgreSQL` for the HTML reports. After successful CI on the repository's default branch, it publishes a tested source ZIP as an Actions artifact; it does not deploy the application.

The current sprint suite covers Stories 1–48 on SQLite and PostgreSQL. Earlier implementation verification also included Chromium checks for desktop, tablet, mobile, and JavaScript-free login. See [the Sprint 4–5 notes](docs/SPRINTS_4_5_IMPLEMENTATION.md). This package has not been pushed, merged or deployed to your GitHub repository.

See [STORIES_1_12.md](docs/STORIES_1_12.md) for BCE mappings and [CHANGES_FROM_5.md](docs/CHANGES_FROM_5.md) for integration notes.

## Designer stories 13–29

Company profiles, designer login/logout, and new/past projects have BCE Python classes, working HTML screens based on the screenshots in `Nothinghere/`, and retained JSON request/display adapters. Code is grouped into `company/`, `designer/`, and `projects/` packages in the relevant layers; see [the class/method map and endpoint guide](docs/STORIES_13_29.md). The later category stories are now implemented: designers select a saved category, and entities reject nonexistent categories. Open `/designer/login` for Staff sign-in or `/designer` for the dashboard. See [the frontend notes](docs/FRONTEND_IMPLEMENTATION.md) for page organization and screenshot scope.

Run `.venv/bin/python -m flask --app app upgrade-db` to create the two new tables in the intended development database without resetting existing records. Run `.venv/bin/python -m pytest tests -q` to check all stories. Existing Stories 1–12 HTML routes remain available.

## Customer and platform manager stories 30–48

Open `/login` or `/staff/login` for Staff sign-in, with User Admin, Interior Designer, and Platform Manager roles. Choose Customer on the slider or open `/customer/login`. Customer and manager dashboards are `/customer` and `/manager`. Designer view/shortlist counts are linked in the designer sidebar.

Customer search/view/save/remove flows, category management, and daily/weekly/monthly report snapshots with CSV downloads are implemented from the Word document and wireframes. Code uses matching `customer/`, `platform_manager/`, `categories/`, `reports/`, and `shortlist/` feature folders. Boundaries validate inputs, controllers relay, and entities own saved data and duplicate checks. See [SPRINTS_4_5_IMPLEMENTATION.md](docs/SPRINTS_4_5_IMPLEMENTATION.md) for exact diagram mappings, report interfaces, routes, and database changes.

The database upgrade preserves existing records. Create a category from the manager portal before adding a designer project. Admin-created accounts still need a password configured with the existing `reset-password` terminal command before their first login.

## BCE diagram audit

All 48 diagrams in the updated report (4) have been reviewed against the code. See [the story-by-story audit](docs/BCE_AUDIT_1_48.md) for exact class/method mappings, layer responsibilities, and the previously approved password-free Story 6 exception. Report classes now use `DailyReportPage`, `WeeklyReportPage`, and `MonthlyReportPage`, each with its diagram event and `displayReport(report)`.
