# Nestora — User Admin stories 1–12

This package adds seven stories to the existing five profile stories: create, view, update, suspend and search user accounts; User Admin login; and logout. It contains the combined Flask application, PostgreSQL models, BCE classes, templates, tests and GitHub Actions workflow. Later stories from the report are outside this package.

## Add this to your existing Codespace

1. Save your current work and use a working branch. Extract the ZIP outside your repository, then merge its files into the repository root (the folder containing `app.py`). Review the diff before committing, especially if teammates have changed the same files.
2. Keep your existing `.env`, `.postgres-data`, `.venv` and `.devcontainer` configuration. This package does not replace your working container setup or contain your database. Do not delete or reinitialize the database. Back up your existing database before changing its schema.
3. In the Codespace terminal, from the repository root, install the application and test dependencies:

   ```bash
   .venv/bin/python -m pip install -r requirements-dev.txt
   ```

   If this is a fresh Codespace without a virtual environment, first run `python -m venv .venv`. The new application dependency is `email-validator`; the requirements files install it automatically.

4. Check the existing `.env`. Keep the same database credentials and `SECRET_KEY`. Set `PROFILE_DEVELOPMENT_PREVIEW=false`. The normal application now requires a real account; the old preview setting cannot bypass login. Use `COOKIE_SECURE=true` with your HTTPS Codespaces forwarded URL, or `false` for local HTTP.
5. With the database service running, apply the non-destructive upgrade:

   ```bash
   .venv/bin/python -m flask --app app upgrade-db
   ```

   This keeps profile records and creates the account/authentication tables. It supports the earlier four-column profile table and adds `status` when missing. An unfamiliar existing account schema stops the upgrade rather than deleting or converting records silently. Review a migration if that message appears.

6. Create the first administrator from the terminal:

   ```bash
   .venv/bin/python -m flask --app app bootstrap-admin
   ```

   Enter a username, email, phone number and a private password of 12–128 characters. Password input is hidden. This command creates any missing standard roles and explicitly activates the `User Admin` profile with the ten profile/account permissions. Other existing profiles keep their permissions. There is no default administrator password. Run it once per initial account, not every time you start the app.

7. Start the app:

   ```bash
   .venv/bin/python -m flask --app app run --host=0.0.0.0 --port=5000
   ```

   Open the forwarded **5000** port and sign in at `/login`. Use the sidebar to manage accounts and profiles. You do not need to rebuild the container for Python, HTML or CSS edits. Rebuild only when its configuration or container-level dependencies change.

For a completely fresh Codespace, your gitignored `.env` will not be copied from another Codespace. Restore the correct database settings before rebuilding your existing Compose setup. `python scripts/setup_env.py` can add missing settings but cannot recover an existing database password. It preserves values already present, including old preview values that you should set to false yourself. Keep `.env` out of Git.

Profile BCE modules live in `boundary/profile/`, `control/profile/`, and `entity/profile/`. Stories 6–10 use the matching `accounts/` packages in those three layers. Each story has its own page and controller file; account data and field validation live in `entity/accounts/`. Profile/account pages collect input directly from HTML, while controllers authorize and relay requests to entities.

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
| 12 | End the current authenticated session | Sidebar **Sign out** (POST `/logout`) |

Account creation collects username, full name, email, phone number and assigned profile. The Create User Account form has no Password or Confirm Password fields, and submissions do not need a password. The server generates the ID and an `Active` status. New account IDs combine the selected profile's actual database ID with a shared account number, padded to at least two digits: profile `1` + account `01` = `101`; profile `2` + account `02` = `202`; profile `3` + account `03` = `303`; another profile `2` account with number `04` = `204`. The number increases across all profiles, rather than restarting for each role. Profile names do not determine the prefix. Existing databases may have different profile IDs from these examples.

The account number grows beyond two digits after 99 (profile `2` + account `100` = `2100`). Because concatenated numbers can occasionally produce the same complete ID, occupied IDs are skipped. IDs remain fixed when a role is reassigned; the prefix records the profile at creation. Existing accounts keep their previous IDs. The shared counter is created automatically on first use, starting after the number of existing accounts, and is committed in the same transaction as the new account. See [ACCOUNT_ID_UPDATE.md](docs/ACCOUNT_ID_UPDATE.md) for how to apply this update.

New accounts created through the web form have no usable password. Before a newly created User Admin can sign in, a trusted administrator sets a private password through `flask --app app reset-password --username <username>` in the server terminal. Bootstrap still creates the first administrator with a password. Existing stored passwords and login behavior are preserved; there is no default password or password-free sign-in. The final-admin guard counts only admins that have a configured password. See [CREATE_ACCOUNT_UPDATE.md](docs/CREATE_ACCOUNT_UPDATE.md) for the files to copy and setup steps.

Update follows the report's editable fields: full name, email and assigned profile. Username, password, ID, status and stored phone number are not changed through this form. Suspension keeps the account record. Repeated suspension is rejected. A suspended account or profile loses access on the next request.

The profile Search screen retains the requested behavior: all profiles appear initially beneath the search bar, and a submitted query filters that table. An empty submitted profile query shows the existing validation message and all profiles. Account search has its own report requirement: blank or whitespace lists all accounts.

Story 11 covers **User Admin login only**. Customer, Interior Designer and Platform Management accounts can be created and assigned roles; their login/portals belong to later stories. Permissions are still checked separately for each admin operation. Profile suspension remains blocked when any account is assigned, including a suspended account. The final fully authorized User Admin cannot be suspended, reassigned, or stripped of access through profile edits.

Passwords are hashed. Login failures use a generic message, and five failed attempts per username/address in 15 minutes trigger temporary throttling. Sessions last 30 minutes. Logout revokes the current server-side session token, including a copied old cookie; another browser's session remains valid. Password reset or role reassignment invalidates previous sessions. All modifying forms use CSRF protection.

Trusted terminal recovery commands:

```bash
.venv/bin/python -m flask --app app reset-password
.venv/bin/python -m flask --app app prune-auth-records
```

The latter removes expired session/failure records and can be run periodically. Neither command prints passwords.

## Tests and GitHub Actions

```bash
.venv/bin/python scripts/run_profile_tests.py
```

The historical script and `tests/profiles` folder names are retained for compatibility; they now cover all twelve stories. Open `reports/test-results.html` to see each pass or failure. `reports/summary.md` lists individual test IDs, including TC01.1–TC01.4. TC08 and TC09 remain omitted, as requested. See [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) and [TEST_CASES.md](docs/TEST_CASES.md).

The workflow `.github/workflows/profile-ci.yml` runs a SQLite/PostgreSQL matrix on push and pull requests. Its run Summary shows every result. Download `profile-reports-SQLite` or `profile-reports-PostgreSQL` for the HTML reports. After successful CI on the repository's default branch, it publishes a tested source ZIP as an Actions artifact; it does not deploy the application.

Local verification of this package passed **125 tests on SQLite**. PostgreSQL table/index definitions compile with the PostgreSQL dialect; an actual PostgreSQL execution must be confirmed by the supplied CI job. This package has not been pushed, merged or deployed to your GitHub repository.

See [STORIES_1_12.md](docs/STORIES_1_12.md) for BCE mappings and [CHANGES_FROM_5.md](docs/CHANGES_FROM_5.md) for integration notes.
