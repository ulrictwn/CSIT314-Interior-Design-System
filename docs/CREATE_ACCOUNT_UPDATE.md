# Create User Account with a default password

The Create screen collects username, full name, email, phone number, and assigned profile. It requires no password entry. Every new account created through the form receives the default password **`password`**, stored as a hash.

## BCE flow

- The boundary strips ordinary text, calls the controller, and displays the result. The create form shows the default password beside its account details instructions.
- The controller relays `createUserAccount(username, password, fullName, email, phoneNumber, profileId)` to `UserAccount`.
- The entity validates input, checks duplicates and the active profile, generates the numeric ID, hashes the default password, and commits the new account.
- The password argument follows the BCE diagram: the form's POST adapter supplies `password`, while trusted setup can pass an explicit private password. The bootstrap administrator uses the password entered at its prompt.

The form's extra password fields, if submitted manually, are ignored. Passwords are stored in the existing `password_hash` column. The original unusable marker remains recognized for older records.

## Sign in

Create an account, then use its username and **`password`** on the login page matching its profile: User Admin, Interior Designer, Customer, or Platform Manager. New accounts receive an Active status and the existing numeric ID format.

To choose a different private password from the trusted terminal:

```bash
.venv/bin/python -m flask --app app reset-password --username newadmin
```

Replace `newadmin` with the chosen username. The command accepts private passwords of 12–128 characters. The automatic classroom default is assigned separately during account creation.

## Verification and setup

Story 6's test submits the creation form, retrieves the saved account, verifies that the default is hashed, checks it against `password`, and signs in through the Customer login page. Tests remain in `tests/sprint_2/`, with shared isolated-database fixtures in `tests/conftest.py`.

Run all sprint tests and refresh reports:

```bash
.venv/bin/python scripts/run_profile_tests.py
```

Restart Flask to load the updated entity/template. This change uses existing columns and requires no database migration.
