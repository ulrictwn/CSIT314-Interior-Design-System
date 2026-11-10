# BCE implementation map

Source: `Nothinghere/CSIT314 Group Project Report (6).docx`; its BCE diagrams are unchanged from the previous report.

Boundaries receive and strip ordinary input, preserve passwords exactly, and display results/errors. Controllers relay calls/results through their entity object. Entities validate every input field and saved-data rule before performing database operations. Reusable pure checks live in `entity/validation.py` and are also used by trusted Python/CLI calls. This follows the lecturer's rule and the report's TDD statement that validation moved from boundaries into entities.

This classroom demonstration uses ordinary HTML forms and a basic browser session for login/logout. Profile/account pages require an active User Admin login; permissions remain stored profile data. See [the implemented demo scope](BCE_DEMO_SIMPLIFICATION.md).

## Diagram classes and methods

| Story | Boundary | Controller/entity operations |
| --- | --- | --- |
| 1 | `CreateUserProfilePage.onCreate`, `displaySuccess`, `displayError` | `CreateUserProfileController.createUserProfile`; `UserProfile.createUserProfile` / `userProfileExists` |
| 2 | `ViewUserProfilePage.onView`, `displayProfile` | `ViewUserProfileController.getUserProfile`; `UserProfile.getUserProfile` |
| 3 | `UpdateUserProfilePage.onUpdate`, `displaySuccess`, `displayError` | `UpdateUserProfileController.getUserProfile` / `updateUserProfile`; `UserProfile.getUserProfile` / `updateUserProfile` |
| 4 | `SuspendUserProfilePage.onSuspend`, `displaySuccess`, `displayError` | `SuspendUserProfileController.suspendUserProfile`; `UserProfile.suspendUserProfile` |
| 5 | `SearchUserProfilePage.onSearch`, `displayResults` | `SearchUserProfileController.searchUserProfiles`; `UserProfile.searchUserProfiles` |
| 6 | `CreateUserAccountPage.onCreate`, `displaySuccess`, `displayError` | `CreateUserAccountController.createUserAccount`; `UserAccount.createUserAccount` / `userAccountExists` / `generateAccountId` |
| 7 | `ViewUserAccountPage.onView`, `displayAccount` | `ViewUserAccountController.getUserAccount`; `UserAccount.getUserAccount` |
| 8 | `UpdateUserAccountPage.onUpdate`, `displaySuccess`, `displayError` | `UpdateUserAccountController.updateUserAccount` (prefill uses ViewUserAccountController); `UserAccount.getUserAccount` / `updateUserAccount` |
| 9 | `SuspendUserAccountPage.onSuspend`, `displaySuccess` | `SuspendUserAccountController.suspendUserAccount`; `UserAccount.suspendUserAccount` |
| 10 | `SearchUserAccountPage.onSearch`, `displayResults` | `SearchUserAccountController.searchUserAccounts`; `UserAccount.searchUserAccounts` |
| 11 | `UserAdminLoginPage.onLogin`, `displayDashboard`, `displayError` | `UserAdminLoginController.login`; `UserAccount.login` |
| 12 | `LogoutPage.logout`, `displayLoginPage` | The report leaves the control/entity methods blank; the boundary clears the browser session and redirects to login. |

Event/display methods return `None` (UML void) and store the response in `self.rendered_page`. Flask's `get()`/`post()` adapters return that response. Create/update/suspend/login entity operations return Boolean results; boundaries display validation and saved-data errors from the controller's entity. Controllers do not duplicate validation or copy entity error fields.

Profile update now uses the diagram's four arguments: `profileId, profileName, description, permissions`. `getUserProfile` remains in the update controller/entity as requested so saved data can be displayed first. Update preserves status; the separate Suspend operation changes it.

## Where validation happens

- Boundary diagram events use only `strip_input` from `boundary/validation.py`. They pass stripped ordinary values and unchanged passwords through controllers without rejecting missing, malformed or overlong fields.
- Entity operations call the pure checks in `entity/validation.py` for required fields, lengths, email/phone formats, supported choices, identifiers and search text. The former `infrastructure/validation.py` module is removed.
- Login boundaries strip the username and preserve the password exactly. `UserAccount.login` validates credential fields, then checks the stored password, account/profile status and role. The shared Staff selector uses `StaffLoginController.selectRole` to relay role validation to `UserAccount.staffRole`.
- Entities check case-insensitive duplicates, uniqueness, active profile references, missing records and saved state, and manage persistence and rollback.
- Initial profile directories and dropdowns use the runtime helper `ViewUserProfileController.listUserProfiles` → `UserProfile.listUserProfiles`. This helper keeps initial listing separate from the diagram's `searchUserProfiles`, which requires submitted search text. Blank account searches still list all accounts. Boundaries display active profile choices; entities verify an assigned profile is active when saving.

## Files

| Area | Location |
| --- | --- |
| Profile boundaries / controls / entity | `boundary/profile/`, `control/profile/`, `entity/profile/user_profile.py` |
| Account boundaries / controls / entity | `boundary/accounts/`, `control/accounts/`, `entity/accounts/user_account.py` |
| Authentication | `boundary/auth/`, `control/auth/`, `entity/accounts/user_account.py` |
| Input cleanup / entity validation | `boundary/validation.py` (only `strip_input`) / `entity/validation.py` |
| HTML | `templates/profiles/`, `templates/accounts/`, `templates/auth/` |
| Routes | `boundary/routes.py` |

The View sidebar entries remain removed. Details are opened from search results; suspend lists retain only the Suspend action. Profile search initially lists all profiles and requires text when a search is submitted; blank account search lists all accounts.

Account creation uses numeric IDs and assigns the hashed default password `password` without a password input field. IDs concatenate the actual profile ID and a shared number padded to at least two digits (`101`, `202`, `303`, `204`). The counter and insert share a transaction, and existing IDs are preserved. Web creation does not accept a password field; the entity assigns the default. Trusted bootstrap/reset input can supply a different private password. Story 6 now includes the diagram's password argument in boundary/controller/entity methods; the POST adapter supplies the default `password` without adding a form field.

Profile/account columns and existing records are preserved. The unused auth_version column remains for database compatibility. Old authentication tables are not dropped or used. Basic portal-role and ownership checks enforce the document's login preconditions. CSRF tokens, rate limiting, server-session tokens/revocation, custom security headers and final-admin protection remain outside the demo scope. Existing password hashes and basic login/logout are retained.

Stories 13–29 are documented in [the designer BCE map](STORIES_13_29.md). Shared test fixtures now live in `tests/conftest.py`; the complete suite is `.venv/bin/python -m pytest tests -q`. `UserAccount.login` accepts an optional profileName for designer login while defaulting to User Admin for the existing flow.
