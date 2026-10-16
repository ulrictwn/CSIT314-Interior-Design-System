# Nestora — user stories 1–5 only

This is the corrected, limited package. Use this ZIP instead of the earlier 48-story ZIP.

## Included scope

1. Create a user profile with name, description, status and selected permission strings.
2. View existing profiles and their details.
3. Update profile information and permissions.
4. Suspend a profile only when no accounts are assigned to it.
5. Search profiles by name or description.

The application uses Boundary, Control and Entity classes. Profile permissions are Python lists, stored as PostgreSQL `text[]`. Checkboxes appear inside a dropdown. Empty selections are allowed and mean no feature permissions. Permissions for future modules can be stored as role data; those modules are not implemented in this package.

No account CRUDS, login/logout, company management, projects, shortlists, categories, reports, test cases or test suite are included.

## Use in your existing Codespace

Keep your existing working `.devcontainer` configuration, `.env`, `.postgres-data`, unrelated code and existing test files. This package contains no replacement container configuration and no real database or credentials. Save or commit your current work before integrating the files.

1. Extract the ZIP. Copy the contents of `nestora-first-five` into your project root, preserving the folder structure. Review overlapping files before replacing them, especially `app.py` and shared infrastructure.
2. Activate your existing virtual environment and install the libraries:

   ```bash
   source .venv/bin/activate
   python -m pip install -r requirements.lock
   ```

   If there is no virtual environment yet, first run `python -m venv .venv`.

3. Keep your current database connection settings. To add missing settings without replacing existing values:

   ```bash
   python scripts/setup_env.py
   ```

   PostgreSQL uses `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, and `POSTGRES_PORT`. Inside your Compose setup the host is normally `db`. An existing `DATABASE_URL` overrides those settings. Keep a stable generated `SECRET_KEY` in `.env`. Do not commit `.env`.

4. Prepare the profile table:

   ```bash
   python -m flask --app app upgrade-db
   ```

   This creates only `user_profile` on a new database. It preserves existing records, adds `status` if missing, and creates a case-insensitive unique-name index. A legacy `user_profiles` table is renamed only if `user_profile` is absent. Duplicate names or an unfamiliar structure stop the upgrade for review. Other existing tables are not deleted.

5. To try these five screens before an account/login module exists, add this line to your local `.env`:

   ```dotenv
   PROFILE_DEVELOPMENT_PREVIEW=true
   ```

   This explicitly enables an unauthenticated development preview. Keep the forwarded Codespaces port **Private**. It is not an implemented login or an authenticated administrator. Leave it `false` when connecting the real authentication described below.

6. Start Flask:

   ```bash
   python -m flask --app app run --host=0.0.0.0 --port=5000
   ```

   Open port 5000 from the Codespaces Ports tab. Visit `/profiles` or `/profiles/create`. Set `COOKIE_SECURE=true` for the HTTPS forwarded URL; use `false` only for local HTTP.

## Existing authentication integration

The report lists “User Admin must be logged in” as a precondition. Implementing account login is outside the requested five stories, so this package provides an integration hook rather than adding that later story. With preview disabled, access is denied until `app.config['PROFILE_ACTOR_LOADER']` is set to a callable that returns your authenticated user, or `None` when signed out. That user must expose `has_permission(code)`. The hook runs on every request. A signed-in admin needs the relevant `profile.create`, `.view`, `.update`, `.suspend`, and `.search` permissions. Register the hook in application setup before serving requests. Do not use a hardcoded user as production authentication.

## Suspension and existing accounts

Story 4 still needs to inspect account assignments. The small adapter in `infrastructure/profile_assignments.py` reads existing `user_account` or `user_accounts` tables with a `profile_id` column. It does not define or create account models, screens, or records. Any assigned account blocks suspension, including a suspended account. The Update status field uses the same guard. When no account table exists yet, there are no stored assignments to block suspension. If your real account table uses another name or foreign-key column, change this adapter before integrating. Future account-assignment code must also lock the profile row and reject a suspended profile.

## Code map

| Story | Boundary | Controller | URL |
| --- | --- | --- | --- |
| 1 | CreateUserProfilePage | CreateUserProfileController | `/profiles/create` |
| 2 | ViewUserProfilePage | ViewUserProfileController | `/profiles`, `/profiles/<id>` |
| 3 | UpdateUserProfilePage | UpdateUserProfileController | `/profiles/<id>/update` |
| 4 | SuspendUserProfilePage | SuspendUserProfileController | `/profiles/<id>/suspend` |
| 5 | SearchUserProfilePage | SearchUserProfileController | `/profiles/search` |

The classes are grouped in `boundary/profile_pages.py` and `control/profile_controllers.py`; matching individual module names re-export them. `entity/user_profile.py` defines persistence. `boundary/forms.py` defines validation. HTML lives in `templates/profiles/` and shared styling in `static/`.

Create/update/suspend use POST and CSRF tokens. Success redirects prevent refresh resubmission. Cancel never saves. Search uses escaped, parameterized matching. Profile names are unique without regard to capitalization. Status is `Active` or `Suspended`. A missing record gives 404; validation gives a visible error and preserves form values. An assigned profile cannot be suspended through either the suspension form or the Update status field.

Local checks cover the five request flows, validation, CSRF, assignment guard, and schema upgrade. No test files or fixtures are shipped. PostgreSQL `text[]` schema compilation was checked; verify the live PostgreSQL connection in your own Codespace. Your GitHub repository has not been edited or pushed.
