# BCE implementation map

User-input validation belongs to the boundary. Controllers relay calls and results. Entities check duplicates and saved-data rules, then perform database operations.

This classroom demonstration uses ordinary HTML forms and a basic browser session for login/logout. Profile/account pages are accessible without signing in; permissions are stored profile data. See [the implemented demo scope](BCE_DEMO_SIMPLIFICATION.md).

## Diagram classes and methods

| Story | Boundary | Controller/entity operations |
| --- | --- | --- |
| 1 | `CreateUserProfilePage.onCreate`, `displaySuccess`, `displayError` | `CreateUserProfileController.createUserProfile` / `userProfileExists`; `UserProfile.createUserProfile` / `userProfileExists` |
| 2 | `ViewUserProfilePage.onView`, `displayProfile`, `displayError` | `ViewUserProfileController.getUserProfile`; `UserProfile.getUserProfile` |
| 3 | `UpdateUserProfilePage.onUpdate`, `displaySuccess`, `displayError` | `UpdateUserProfileController.getUserProfile` / `updateUserProfile`; `UserProfile.getUserProfile` / `updateUserProfile` |
| 4 | `SuspendUserProfilePage.onSuspend`, `displaySuccess`, `displayError` | `SuspendUserProfileController.suspendUserProfile`; `UserProfile.suspendUserProfile` |
| 5 | `SearchUserProfilePage.onSearch`, `displayResults` | `SearchUserProfileController.searchUserProfiles`; `UserProfile.searchUserProfiles` |
| 6 | `CreateUserAccountPage.clickCreate`, `displaySuccess`, `displayError` | `CreateUserAccountController.createUserAccount` / `userAccountExists`; `UserAccount.createUserAccount` / `userAccountExists` / `generateAccountId` |
| 7 | `ViewUserAccountPage.onView`, `displayAccount` | `ViewUserAccountController.getUserAccount`; `UserAccount.getUserAccount` |
| 8 | `UpdateUserAccountPage.onUpdate`, `displaySuccess`, `displayError` | `UpdateUserAccountController.getUserAccount` / `updateUserAccount`; `UserAccount.getUserAccount` / `updateUserAccount` |
| 9 | `SuspendUserAccountPage.onSuspend`, `displaySuccess`, `displayError` | `SuspendUserAccountController.suspendUserAccount`; `UserAccount.suspendUserAccount` |
| 10 | `SearchUserAccountPage.onSearch`, `displayResults` | `SearchUserAccountController.searchUserAccounts`; `UserAccount.searchUserAccounts` |
| 11 | `LoginPage.clickLogin`, `displayDashboard`, `displayError` | `LoginController.login`; `UserAccount.login` |
| 12 | `LogoutPage.logout`, `displayLoginPage` | The report leaves the control/entity methods blank; the boundary clears the browser session and redirects to login. |

Event/display methods return `None` (UML void) and store the response in `self.rendered_page`. Flask's `get()`/`post()` adapters return that response. Create/update/suspend/login entity operations return Boolean results; controllers relay duplicate messages and other saved-data errors to the boundary.

Profile update now uses the diagram's four arguments: `profileId, profileName, description, permissions`. `getUserProfile` remains in the update controller/entity as requested so saved data can be displayed first. Update preserves status; the separate Suspend operation changes it.

## Where validation happens

- `boundary/validation.py` contains plain shared functions, not form classes. It handles whitespace cleanup, required fields, maximum lengths, username/email/phone formats, supported statuses/permission choices, identifier formats, search text, and login field checks. CLI input adapters reuse the same boundary helpers.
- Boundary event methods call those helpers before invoking the corresponding controller operation. Invalid input is displayed with the submitted values and field errors; it does not reach a mutation or search operation in the entity. Read-only lookups may still populate form selections or an error screen.
- Login trims the username and preserves the password exactly. Boundary checks reject missing/whitespace-only fields and overlong values. Matching a submitted password against the saved account remains an entity database responsibility.
- Profile/account entities retain case-insensitive duplicate-name, username, and email checks, including database uniqueness constraints and rollback after competing inserts. No field-format validators remain in those entities.
- Entities retain rules requiring saved data: an assigned profile cannot be suspended, account assignment requires an existing active profile, missing records return an unavailable result, and account updates preserve fields outside the diagram's arguments.

## Files

| Area | Location |
| --- | --- |
| Profile boundaries / controls / entity | `boundary/profile/`, `control/profile/`, `entity/profile/user_profile.py` |
| Account boundaries / controls / entity | `boundary/accounts/`, `control/accounts/`, `entity/accounts/user_account.py` |
| Authentication | `boundary/auth/`, `control/auth/`, `entity/accounts/user_account.py` |
| Shared input checks | `boundary/validation.py` |
| HTML | `templates/profiles/`, `templates/accounts/`, `templates/auth/` |
| Routes | `boundary/routes.py` |

The View sidebar entries remain removed. Details are opened from search results; suspend lists retain only the Suspend action. Profile search initially lists all profiles and requires text when a search is submitted; blank account search lists all accounts.

The confirmed numeric-ID and password-free account creation choices remain in place. IDs concatenate the actual profile ID and a shared number padded to at least two digits (`101`, `202`, `303`, `204`). The counter and insert share a transaction, and existing IDs are preserved. Web creation does not accept a password; trusted bootstrap/reset input can configure one. Password-free administrator creation is the confirmed exception to Story 6's password argument.

Profile/account columns and existing records are preserved. The unused auth_version column remains for database compatibility. Old authentication tables are not dropped or used. Authorization guards, CSRF tokens, rate limiting, server-session tokens/revocation, custom security headers, and final-admin protection were removed from the demo. Existing password hashes and basic login/logout are retained.

Stories 13–29 are documented in [the designer BCE map](STORIES_13_29.md). Shared test fixtures now live in `tests/conftest.py`; the complete suite is `.venv/bin/python -m pytest tests -q`. `UserAccount.login` accepts an optional profileName for designer login while defaulting to User Admin for the existing flow.
