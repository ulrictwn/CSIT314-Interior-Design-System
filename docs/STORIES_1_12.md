# BCE implementation map

For Stories 1–12, boundaries receive user input and display results, controllers relay requests and results, and entities validate data and handle database operations. Profile/account controllers also enforce operation permissions. Shared package modules re-export the per-story classes for grouped imports.

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

Profile modules are grouped into `boundary/profile/`, `control/profile/`, and `entity/profile/`. Account modules are grouped into `boundary/accounts/`, `control/accounts/`, and `entity/accounts/`. For example, import the account model with `from entity.accounts.user_account import UserAccount`.

Login/logout follow the same BCE separation. `LoginPage` and `LogoutPage` handle input, presentation, and browser-session changes; their controllers relay to `UserAccount`, `LoginAttempt`, and `LoginSession`. Credential validation, rate limiting, and server-session database operations belong to entities. Login/logout use plain HTML forms protected by global CSRF validation; the unused form module has been removed. See [the authentication implementation map](AUTH_BCE_REFACTOR_PROPOSAL.md).

## Where to edit the code

| Area | Actual implementation |
| --- | --- |
| Profile boundaries | `boundary/profile/create_user_profile_page.py`, `boundary/profile/view_user_profile_page.py`, `boundary/profile/update_user_profile_page.py`, `boundary/profile/suspend_user_profile_page.py`, `boundary/profile/search_user_profile_page.py`; directory in `boundary/profile/profile_pages.py` |
| Account boundaries | Each story’s `boundary/accounts/*_user_account_page.py`; directory and class re-exports in `boundary/accounts/account_pages.py` |
| Login/logout boundaries | `boundary/auth/login_page.py`, `boundary/auth/logout_page.py`; shared class exports in `boundary/auth/auth_pages.py` |
| Profile controls | Each story's `control/profile/*_user_profile_controller.py`; directory and compatibility imports in `control/profile/profile_controllers.py` |
| Account controls | Each story’s `control/accounts/*_user_account_controller.py`; directory and class re-exports in `control/accounts/account_controllers.py` |
| Login/logout controls | `control/auth/login_controller.py`, `control/auth/logout_controller.py`; shared class exports in `control/auth/auth_controller.py` |
| Profile/account data | `entity/profile/user_profile.py`, `entity/accounts/user_account.py` |
| Forms/routes | Boundaries read `request.form` or `request.args` directly; plain HTML forms include CSRF tokens; routing is in `boundary/routes.py` |
| Account HTML | `templates/accounts/` |
| Login HTML | `templates/auth/login.html` |
| Authentication data | `entity/accounts/user_account.py`, `entity/auth/login_attempt.py`, `entity/auth/login_session.py`; request-loading adapter in `infrastructure/auth.py` |
| Database setup/CLI | `infrastructure/migrations.py`, `infrastructure/commands.py` |

Profile and account story methods live in their individual page/controller files. The shared modules inside each feature package re-export these classes and implement the directory screens. Account field validation helpers live in `entity/accounts/user_account.py`; the entity operations invoke them before reading or writing account records.

## New diagram-facing methods

| Story | Boundary method (returns `None` / UML void) | Control/entity operation |
| --- | --- | --- |
| 1 | `clickCreate(profileName, description, status, permissions)`, `displaySuccess()`, `displayError()` | Controller and entity: `createUserProfile(...) -> bool`, `userProfileExists(profileName) -> bool` |
| 2 | `onView(profileId)`, `displayProfile(profile)`, `displayError()` | Controller and entity: `getUserProfile(profileId) -> UserProfile` (or `None` when unavailable) |
| 3 | `onUpdate(profileId, profileName, description, permissions)`, `displaySuccess()`, `displayError()` | Controller and entity: `getUserProfile(profileId)`, `updateUserProfile(...) -> bool`; optional `status` preserves the current editable status field |
| 4 | `onSuspend(profileId)`, `displaySuccess()`, `displayError()` | Controller and entity: `suspendUserProfile(profileId) -> bool`; a controller getter loads the confirmation page |
| 5 | `onSearch(keyword)`, `displayResults(profiles)` | Controller and entity: `searchUserProfiles(keyword) -> list[UserProfile]`; a list helper loads the initial page |
| 6 | `clickCreate(username, fullName, email, phoneNumber, profileId)`, `displaySuccess()`, `displayError()` | `createUserAccount(...) -> bool`, `userAccountExists(username) -> bool`; entity `generateAccountId(profileId) -> str` |
| 7 | `onView(accountId)`, `displayAccount(account)` | Controller/entity: `getUserAccount(accountId) -> UserAccount` or `None`; boundary displays 404 for an unavailable account |
| 8 | `onUpdate(accountId, fullName, email, profileId)`, `displaySuccess()`, `displayError()` | Controller/entity: `getUserAccount(accountId)` for form prefill and `updateUserAccount(...) -> bool` |
| 9 | `onSuspend(accountId)`, `displaySuccess()`, `displayError()` | Controller/entity: `suspendUserAccount(accountId) -> bool`; getter loads confirmation details |
| 10 | `onSearch(keyword)`, `displayResults(accounts)` | Controller/entity: `searchUserAccounts(keyword) -> list[UserAccount]` |
| 11 | `clickLogin(username, password)`, `displayDashboard()`, `displayError()` | `login(username, password) -> bool`; constructor context supplies address, attempt limit, previous token, and lifetime |
| 12 | `logout()`, `displayLoginPage()` | Controller forwards revocation to `LoginSession.revoke`; boundary clears the browser session |

Boundary event methods store the rendered response on `self.rendered_page`; Flask's `get()`/`post()` adapters return it. This preserves the UML void signatures without preventing HTTP responses. Creation, update, suspension, and login return `False` for rejected operations; controllers relay entity error messages, field errors, and failure reasons; boundaries choose the HTTP response and presentation. Other operations can raise `DomainError`; authorization and not-found errors map to 403/404. Successful entity writes commit before returning `True`.

Story 2 opens profile details from the View button in search results. The View User Profiles sidebar entry is removed; search and view retain their separate permissions. The detail page links back to search when the actor has search access, and otherwise links to the existing profile directory. `get()` adapts HTTP requests to the diagram's void `onView`, `displayProfile`, and `displayError` methods. The view controller only authorizes and forwards the lookup. `UserProfile.getUserProfile` validates a positive database integer ID before querying, returning `None` for invalid or missing profiles so the boundary can display a 404. The shared modules inside the profile packages also re-export the per-story classes.

Story 3 loads the saved profile through `UpdateUserProfileController.getUserProfile` and `UserProfile.getUserProfile` before displaying the update form. The boundary receives edits directly from HTML. The diagram's four main arguments are supported; the optional boolean status argument preserves the existing status control, and omitting it preserves the stored status. Missing or unsupported HTML status values are passed to the entity for rejection. The entity validates all edits before querying, checks uniqueness, locks the row, enforces assignment and final-admin rules, and commits or rolls back the operation.

Story 4 loads the profile for confirmation through its controller, submits with a CSRF token, and delegates suspension to the entity. The entity rejects invalid or missing IDs and profiles assigned to any account, including suspended accounts. Legacy assignment-table checks remain in place. Rejections return `False` with an entity message, including “This profile is in use.”

Story 5 reads the query string in its boundary and passes the keyword through the controller. Required-text and 200-character limits are enforced in `UserProfile.searchUserProfiles`. Matching remains case-insensitive across names and descriptions, with SQL wildcard characters treated literally. Empty submissions display the entity's error message, initial pages list all profiles, and no matches display “No profiles found.”

Story 11 uses `LoginPage.clickLogin` to call `LoginController.login`, which delegates credential/status/role and rate-limit checks to `UserAccount().login` and session creation to `LoginSession.start`. The boundary chooses the dashboard redirect or error display. `LoginAttempt` handles failed-attempt records, and `LoginSession` handles hashed tokens, expiry, auth-version checks, and revocation. Story 12 keeps authenticated, CSRF-protected POST logout: the controller revokes the current token through the entity, and the boundary clears the browser session and displays login. Other browser sessions remain active.

Stories 6–10 follow the same separation as profiles. Boundaries receive raw HTML form/query values, call the controller, and choose the rendered result or redirect. Controllers only check authorization and relay entity requests, booleans, account objects, lists, and error details. Create/update/suspend operations are called on a `UserAccount()` instance, with instance-local failure information and no HTTP codes in the entity. Reads and ID generation remain class methods. Global CSRF protection validates tokens included by the plain HTML forms.

Story 6 validates username syntax, required fields and lengths, email format, phone format, case-insensitive username/email uniqueness, and an active assigned profile inside the entity. `generateAccountId` allocates the shared numeric sequence in the same transaction as the account insert. Failed writes roll back the allocation. The report's password argument and older letter-based ID examples remain superseded by the documented password-free creation and numeric-ID requirements below. Trusted setup alone can pass the entity's optional keyword-only password.

Story 7 is opened through the View button in account search results. The View User Accounts sidebar entry is removed, and details link back to search when the actor has search permission (otherwise back to the account directory). The account is retrieved through the controller and entity before display, including its assigned role. Password data is never rendered. Story 8 also retrieves saved account data through `getUserAccount` to populate the edit screen. The entity validates edits, checks email uniqueness and active role assignment, and preserves account ID, username, phone, password, and status. Role changes increment `auth_version` so earlier sessions stop working. Last-usable-admin checks remain enforced inside the entity.

Story 9 confirms the account details before suspension, rejects already suspended accounts with the existing message, preserves stored account data, and invalidates earlier sessions. Story 10 validates the keyword type/length in the entity and searches ID, username, and full name case-insensitively. Blank or whitespace queries list all accounts. Names and submitted field values are escaped by HTML templates, and errors preserve form input and profile selection.

## Data and permissions

Story 1 follows the report's BCE diagram: status is a boolean at the boundary event, controller, and entity creation method (`True` = Active, `False` = Suspended). The boundary reads `request.form` directly and converts the existing HTML status option values to booleans. The entity maps them to the existing database strings, so no database migration is required. `UserProfile().createUserProfile(...)` validates before querying, checks duplicates through `userProfileExists`, commits on success, and rolls back failed database writes. Errors belong to that entity instance and are relayed by the controller. The creation template defines the HTML fields, restores submitted values, displays entity errors, and includes a CSRF token protected by the application’s global `CSRFProtect`. No creation form class is needed; the entity owns required-field, length, status, permission, and uniqueness rules. The update and suspend pages also use plain HTML with CSRF tokens; no profile-specific FlaskForm classes are needed.

The existing singular `user_profile` table retains its permissions list (`text[]` on PostgreSQL, JSON in isolated SQLite tests). `user_account.profile_id` references that table; one account has one assigned profile. The new auxiliary tables are `account_id_counter`, `login_session` and `login_attempt`.

The five `account.*` codes mirror the five existing `profile.*` operations. Existing permission choices for future features remain in the catalog so old selected values are not lost; they do not add those future features to this application. Bootstrap grants the initial User Admin all ten implemented codes.

`User Admin` is the canonical admin role name used by this twelve-story portal. Additional admin accounts should be assigned that role. The later requested account-ID format supersedes the report's letter-prefix examples: use the actual profile ID followed by a shared account number padded to at least two digits (`101`, `202`, `303`, `204`). Password length, email uniqueness and the final-admin guard are unchanged.

The existing `account_id_counter` schema is reused. Its `*` row supplies one global sequence starting at `1` on an empty database; older per-role rows are retained but unused. On an existing installation, the initial shared number starts at the current account count plus one. PostgreSQL row locks serialize allocation, and the account creation transaction commits or rolls back both the counter and account together. Existing IDs are retained, and IDs stay fixed after role reassignment. Numbers can grow beyond 99; occupied complete IDs are skipped to handle ambiguity from concatenating variable-length numbers.


The later password-free creation request also supersedes the Password field in the original wireframe. The boundary/controller creation methods take username, fullName, email, phoneNumber and profileId only. The entity has the same required arguments plus an optional keyword-only `password` for trusted bootstrap code. Web input never supplies that keyword. Accounts created without it receive an unusable-password marker in the existing non-null password_hash column; no schema alteration is required. Login rejects those accounts until the trusted reset-password command sets a real hash. The final-admin guard requires a configured password when counting usable administrators.
