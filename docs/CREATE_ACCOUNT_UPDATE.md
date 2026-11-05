# Create User Account without password entry

The Create screen collects username, full name, email, phone number and assigned profile. Account code is grouped under the `accounts/` packages in boundary, control, and entity. Input cleanup and field validation belong to `boundary/validation.py` and are called by the boundary before the controller. Duplicate checks and persistence belong to `entity/accounts/user_account.py`.

## Apply the matching files together

Stop Flask with Ctrl+C. Review any local/team edits, then copy these application files from this package into the existing project folders:

- The complete `boundary/accounts/`, `control/accounts/`, and `entity/accounts/` packages, including `__init__.py` and the shared boundary validation helpers.
- `boundary/routes.py`, `boundary/dashboard_page.py`, and the plain HTML account forms under `templates/accounts/`.
- `control/auth/auth_controller.py`, `entity/models.py`, and `entity/profile/user_profile.py` for updated account imports.
- `infrastructure/auth.py` and `infrastructure/commands.py`.
- `templates/accounts/form.html` and `templates/accounts/suspend.html`.

Copy the updated `tests/profiles/` files together too; their account imports use the new packages, and `test_accounts_bce.py` covers the separation and validation contracts. The historical test-folder name is retained.

No new library or database-schema change is needed for this update to the existing twelve-story app. Preserve `.env`, the database, `.venv` and the working devcontainer configuration. Existing passwords, profile/account records and numeric ID counters continue to work. This source package has not changed your GitHub repository automatically.

Restart Flask:

```bash
.venv/bin/python -m flask --app app run --host=0.0.0.0 --port=5000
```

Create an account through the form and verify that it is saved without password entry. Numeric account IDs still use the requested shared sequence, for example 101, 202, 303 and 204.

Run the combined tests:

```bash
.venv/bin/python scripts/run_profile_tests.py
```

## Giving a new User Admin sign-in access

Creating an account saves its details and an Active status. It does not set a usable password. User Admin login still requires a valid password, and newly created accounts cannot sign in until one is set through the existing trusted terminal command:

```bash
.venv/bin/python -m flask --app app reset-password --username newadmin
```

Replace `newadmin` with the created username. Enter and confirm a private password of 12–128 characters. Password input is hidden. The initial `bootstrap-admin` command still asks for a password so the first administrator can sign in immediately.

Customer/Designer/Platform Management login remains outside these twelve user stories, as before. Setting their password does not grant access to the User Admin portal.

## Storage and access rules

The existing non-null `password_hash` field is retained. Accounts created without a password store an unusable marker, rather than a default password or a hash of an empty password. A submitted extra password field is ignored by the Create page. Configured passwords continue to be hashed.

Only active, fully authorized User Admin accounts with a configured password count toward the final-admin access guard. This prevents an unconfigured new admin from allowing the only usable administrator to lose access.
