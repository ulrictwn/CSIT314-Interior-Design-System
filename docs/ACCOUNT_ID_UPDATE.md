# Profile ID + shared account number

This update applies the requested numeric account-ID format to future account creation.

| Order created | Actual profile ID | Shared account number | Generated account ID |
| --- | --- | --- | --- |
| 1 | 1 (User Admin in this example) | 01 | 101 |
| 2 | 2 (Customer) | 02 | 202 |
| 3 | 3 (Interior Designer) | 03 | 303 |
| 4 | 2 (another Customer) | 04 | 204 |

The prefix comes from the stored `user_profile.profile_id`, so it works with renamed profiles and custom roles. If your existing User Admin profile has ID 5, its prefix is 5. The examples do not renumber your profiles.

## Apply to the working twelve-story app

The ID-generation change is in `entity/accounts/user_account.py`. The latest package also includes the later request for password-free account creation, which changes the method signature across boundary/control/entity and the trusted bootstrap caller. Apply the matching files listed in [CREATE_ACCOUNT_UPDATE.md](CREATE_ACCOUNT_UPDATE.md) together when upgrading from the earlier package. No new library is required.

The current basic account-creation test is `tests/sprint_2/test_story_06_create_user_account.py`, with view/update/suspend/search tests in the same sprint folder. The earlier dedicated counter edge-case suite was removed during the requested simplification. Shared fixtures remain in `tests/conftest.py`; see [the test guide](TESTING_GUIDE.md).

README and the docs describe the revised behavior. Other application files in this package are the same combined twelve-story version delivered earlier; review local/team changes before replacing them.

Keep the current database, `.env`, virtual environment and devcontainer configuration. If you already have the twelve-story tables, the existing counter table is reused and its shared row is created automatically. If those tables have not been set up, run:

```bash
.venv/bin/python -m flask --app app upgrade-db
```

Stop Flask with Ctrl+C, then restart it:

```bash
.venv/bin/python -m flask --app app run --host=0.0.0.0 --port=5000
```

Create an account through the normal account form. Run the combined tests with:

```bash
.venv/bin/python scripts/run_profile_tests.py
```

## Existing IDs and sequence behavior

- Existing accounts retain their IDs, including IDs such as `UA101` and `CU101`. This preserves stored references. Future accounts use the numeric format.
- On the first allocation in an existing installation, the shared number starts at the existing account count plus one. For example, one existing account means the next number is `02`. Subsequent allocations use the saved counter, even when the account's profile differs.
- A successful bootstrap administrator creation also consumes a number. Re-running bootstrap is not needed to enable this update.
- The suffix is at least two digits. It expands after `99`; profile 2 with number 100 gets `2100`. Existing complete IDs are skipped if concatenation would duplicate them.
- Creation commits the account and counter together. A rejected database write rolls the allocation back. Concurrent creation is serialized using the shared counter.
- Account IDs remain fixed after profile reassignment. The stored `profile_id` gives the current role; the account-ID prefix records the role at creation.

The account-ID column remains a string so old IDs and references continue to work. New generated values contain only digits.
