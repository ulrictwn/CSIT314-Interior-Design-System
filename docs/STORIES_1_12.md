# BCE implementation map

Boundaries receive input and strip ordinary text. Controllers relay calls/results through their entity object. Entities validate fields, formats, lengths, duplicates, references, and saved state, then perform database operations.

This classroom demonstration uses ordinary HTML forms and a basic browser session for login/logout. Profile/account pages require an active User Admin login; permissions remain stored profile data. See [the implemented demo scope](BCE_DEMO_SIMPLIFICATION.md).

## Diagram classes and methods

| Story | Boundary | Controller/entity operations |
| --- | --- | --- |
| 1 | `CreateUserProfilePage.onCreate`, `displaySuccess`, `displayError` | `CreateUserProfileController.createUserProfile`; `UserProfile.createUserProfile` / `userProfileExists` |
| 2 | `ViewUserProfilePage.onView`, `displayProfile` | `ViewUserProfileController.getUserProfile`; `UserProfile.getUserProfile` |
| 3 | `UpdateUserProfilePage.onUpdate`, `displaySuccess`, `displayError` | `UpdateUserProfileController.getUserProfile` / `updateUserProfile`; `UserProfile.getUserProfile` / `updateUserProfile` |
| 4 | `SuspendUserProfilePage.onSuspend`, `displaySuccess`, `displayError`, `displayError` | `SuspendUserProfileController.suspendUserProfile`; `UserProfile.suspendUserProfile` |
| 5 | `SearchUserProfilePage.onSearch`, `displayResults` | `SearchUserProfileController.searchUserProfiles`; `UserProfile.searchUserProfiles` |
| 6 | `CreateUserAccountPage.onCreate`, `displaySuccess`, `displayError` | `CreateUserAccountController.createUserAccount`; `UserAccount.createUserAccount` / `userAccountExists` / `generateAccountId` |
| 7 | `ViewUserAccountPage.onView`, `displayAccount` | `ViewUserAccountController.getUserAccount`; `UserAccount.getUserAccount` |
| 8 | `UpdateUserAccountPage.onUpdate`, `displaySuccess`, `displayError` | `UpdateUserAccountController.getUserAccount` / `updateUserAccount`; `UserAccount.getUserAccount` / `updateUserAccount` |
| 9 | `SuspendUserAccountPage.onSuspend`, `displaySuccess`, `displayError` | `SuspendUserAccountController.suspendUserAccount`; `UserAccount.suspendUserAccount` |
| 10 | `SearchUserAccountPage.onSearch`, `displayResults` | `SearchUserAccountController.searchUserAccounts`; `UserAccount.searchUserAccounts` |
| 11 | `UserAdminLoginPage.onLogin`, `displayDashboard`, `displayError` | `UserAdminLoginController.login`; `UserAccount.login` |
| 12 | `LogoutPage.logout`, `displayLoginPage` | The report leaves the control/entity methods blank; the boundary clears the browser session and redirects to login. |

Event/display methods return `None` (UML void) and store the response in `self.rendered_page`. Flask's `get()`/`post()` adapters return that response. Create/update/suspend/login entity operations return Boolean results; controllers relay duplicate messages and other saved-data errors to the boundary.

Profile update now uses the diagram's four arguments: `profileId, profileName, description, permissions`. `getUserProfile` remains in the update controller/entity as requested so saved data can be displayed first. Update preserves status; the separate Suspend operation changes it.

## Where validation happens

- `boundary/validation.py` contains only `strip_input`. Boundary event methods trim ordinary text, call controllers, and display the submitted values and entity errors.
- `entity/validation.py` contains shared required-field, length, format, status, permission-choice, identifier, search, and login checks. Entity operations invoke these helpers themselves, so direct calls are validated too. CLI input adapters reuse the entity helpers.
- Login strips the username and preserves the password exactly. `UserAccount.login` validates credential input before checking the saved password, account/profile status, and role.
- Profile/account entities handle case-insensitive duplicates, database uniqueness constraints, rollback, active profile assignment, missing records, and preservation of fields outside the diagram arguments.
- `UserProfile.activeProfiles()` supplies the account dropdowns. Controllers relay the operation and keep `self.entity`; the boundary reads that entity's errors. Basic portal access checks use the saved session and reject wrong roles or forged account context.

## Files

| Area | Location |
| --- | --- |
| Profile boundaries / controls / entity | `boundary/profile/`, `control/profile/`, `entity/profile/user_profile.py` |
| Account boundaries / controls / entity | `boundary/accounts/`, `control/accounts/`, `entity/accounts/user_account.py` |
| Authentication | `boundary/auth/`, `control/auth/`, `entity/accounts/user_account.py` |
| Input cleanup / validation | `boundary/validation.py` / `entity/validation.py` |
| HTML | `templates/profiles/`, `templates/accounts/`, `templates/auth/` |
| Routes | `boundary/routes.py` |

The View sidebar entries remain removed. Details are opened from search results; suspend lists retain only the Suspend action. Profile search initially lists all profiles and requires text when a search is submitted; blank account search lists all accounts.

Account creation uses numeric IDs and assigns the hashed default password `password` without a password input field. IDs concatenate the actual profile ID and a shared number padded to at least two digits (`101`, `202`, `303`, `204`). The counter and insert share a transaction, and existing IDs are preserved. Web creation does not accept a password field; the entity assigns the default. Trusted bootstrap/reset input can supply a different private password. Story 6 now includes the diagram's password argument in boundary/controller/entity methods; the POST adapter supplies the default `password` without adding a form field.

Profile/account columns and existing records are preserved. The unused auth_version column remains for database compatibility. Old authentication tables are not dropped or used. Authorization guards, CSRF tokens, rate limiting, server-session tokens/revocation, custom security headers, and final-admin protection were removed from the demo. Existing password hashes and basic login/logout are retained.

Stories 13–29 are documented in [the designer BCE map](STORIES_13_29.md). Shared test fixtures now live in `tests/conftest.py`; the complete suite is `.venv/bin/python -m pytest tests -q`. `UserAccount.login` accepts an optional profileName for designer login while defaulting to User Admin for the existing flow.
