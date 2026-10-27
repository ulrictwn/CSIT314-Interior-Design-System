# BCE implementation map

The boundary handles HTTP forms, the control validates and authorizes the operation, and the entity reads/writes stored data. Public per-story modules re-export classes from shared files so existing imports still work.

| Story | Boundary class | Control class | Entity |
| --- | --- | --- | --- |
| 1 | CreateUserProfilePage | CreateUserProfileController | UserProfile |
| 2 | ViewUserProfilePage | ViewUserProfileController | UserProfile |
| 3 | UpdateUserProfilePage | UpdateUserProfileController | UserProfile |
| 4 | SuspendUserProfilePage | SuspendUserProfileController | UserProfile |
| 5 | SearchUserProfilePage | SearchUserProfileController | UserProfile |
| 6 | CreateUserAccountPage | CreateUserAccountController | UserAccount |
| 7 | ViewUserAccountPage | ViewUserAccountController | UserAccount |
| 8 | UpdateUserAccountPage | UpdateUserAccountController | UserAccount |
| 9 | SuspendUserAccountPage | SuspendUserAccountController | UserAccount |
| 10 | SearchUserAccountPage | SearchUserAccountController | UserAccount |
| 11 | LoginPage | LoginController | UserAccount |
| 12 | LogoutPage | LogoutController | LoginSession |

## Where to edit the code

| Area | Actual implementation |
| --- | --- |
| Profile boundaries | `boundary/profile_pages.py` |
| Account boundaries | `boundary/account_pages.py` |
| Login/logout boundaries | `boundary/auth_pages.py` |
| Profile controls | `control/profile_controllers.py` |
| Account controls | `control/account_controllers.py` |
| Login/logout controls | `control/auth_controller.py` |
| Profile/account data | `entity/user_profile.py`, `entity/user_account.py` |
| Forms/routes | `boundary/forms.py`, `boundary/routes.py` |
| Account HTML | `templates/accounts/` |
| Login HTML | `templates/auth/login.html` |
| Session loading and revocation | `infrastructure/auth.py`, `entity/login_session.py` |
| Database setup/CLI | `infrastructure/migrations.py`, `infrastructure/commands.py` |

For example, `boundary/search_user_account_page.py` contains an import, while the class's method bodies are in `boundary/account_pages.py`. This is the same import arrangement used for the existing profile screens.

## New diagram-facing methods

| Story | Boundary method (returns `None` / UML void) | Control/entity operation |
| --- | --- | --- |
| 6 | `clickCreate(username, fullName, email, phoneNumber, profileId)` | `createUserAccount(...) -> bool`, `userAccountExists(username) -> bool`; entity `generateAccountId(profileId) -> str` |
| 7 | `onView(accountId)`, `displayAccount(account)` | `getUserAccount(accountId) -> UserAccount` or a not-found error |
| 8 | `onUpdate(accountId, fullName, email, profileId)` | `updateUserAccount(...) -> bool` |
| 9 | `onSuspend(accountId)` | `suspendUserAccount(accountId) -> bool` |
| 10 | `onSearch(keyword)`, `displayResults(accounts)` | `searchUserAccounts(keyword) -> list` |
| 11 | `clickLogin(username, password)`, `displayDashboard()`, `displayError()` | `login(username, password) -> bool`; control also receives an optional address for throttling |
| 12 | `logout()`, `displayLoginPage()` | Revoke current token and clear the session |

Boundary event methods store the rendered response on `self.rendered_page`; Flask's `get()`/`post()` adapters return it. This preserves the UML void signatures without preventing HTTP responses. Validation errors raise `DomainError`; authorization and not-found errors map to 403/404. Successful entity writes commit before returning `True`.

## Data and permissions

The existing singular `user_profile` table retains its permissions list (`text[]` on PostgreSQL, JSON in isolated SQLite tests). `user_account.profile_id` references that table; one account has one assigned profile. The new auxiliary tables are `account_id_counter`, `login_session` and `login_attempt`.

The five `account.*` codes mirror the five existing `profile.*` operations. Existing permission choices for future features remain in the catalog so old selected values are not lost; they do not add those future features to this application. Bootstrap grants the initial User Admin all ten implemented codes.

`User Admin` is the canonical admin role name used by this twelve-story portal. Additional admin accounts should be assigned that role. The later requested account-ID format supersedes the report's letter-prefix examples: use the actual profile ID followed by a shared account number padded to at least two digits (`101`, `202`, `303`, `204`). Password length, email uniqueness and the final-admin guard are unchanged.

The existing `account_id_counter` schema is reused. Its `*` row supplies one global sequence starting at `1` on an empty database; older per-role rows are retained but unused. On an existing installation, the initial shared number starts at the current account count plus one. PostgreSQL row locks serialize allocation, and the account creation transaction commits or rolls back both the counter and account together. Existing IDs are retained, and IDs stay fixed after role reassignment. Numbers can grow beyond 99; occupied complete IDs are skipped to handle ambiguity from concatenating variable-length numbers.


The later password-free creation request also supersedes the Password field in the original wireframe. The boundary/controller creation methods take username, fullName, email, phoneNumber and profileId only. The entity has the same required arguments plus an optional keyword-only `password` for trusted bootstrap code. Web input never supplies that keyword. Accounts created without it receive an unusable-password marker in the existing non-null password_hash column; no schema alteration is required. Login rejects those accounts until the trusted reset-password command sets a real hash. The final-admin guard requires a configured password when counting usable administrators.
