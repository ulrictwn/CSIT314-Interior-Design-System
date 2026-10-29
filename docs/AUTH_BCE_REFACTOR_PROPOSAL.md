# Login and logout BCE implementation

Stories 11 and 12 follow the report's BCE structure. Boundaries receive input and display responses, controllers relay requests and results, and entities validate credentials and handle authentication data. The supporting authentication classes live under `boundary/auth/`, `control/auth/`, and `entity/auth/`; `UserAccount` remains in `entity/accounts/`.

## Responsibilities and methods

| File | Responsibility |
| --- | --- |
| `boundary/auth/login_page.py` | `post()` reads `request.form` and calls `clickLogin(username, password) -> None`. That event calls the controller, then invokes `displayDashboard() -> None` or `displayError() -> None`. On success, it stores entity-produced login data in Flask's browser session. On failure, it retains only the username and displays entity errors. |
| `control/auth/login_controller.py` | `login(username, password) -> bool` forwards credentials and configuration to `UserAccount().login`, relays errors, and asks `LoginSession.start` to create a session on success. Its constructor receives request address, attempt limit, previous token, and session lifetime from the boundary. It contains no input validation, SQL, or Flask session mutation. |
| `entity/accounts/user_account.py` | `validateLoginCredentials` owns the previous form/controller required-field and length checks. `login(username, password, *, remote_address='', attempt_limit=5) -> bool` checks credentials, account/profile status, User Admin role, and rate limiting. Rejections return `False` with instance-local error details; success exposes `authenticated_account`. Login is now an instance method, like account mutations. |
| `entity/auth/login_attempt.py` | `keyFor`, `isLimited`, `recordFailure`, and `clearFailures` own failed-attempt keys, the 15-minute window, limit decisions, and their database operations. |
| `entity/auth/login_session.py` | `start`, `tokenHash`, `getAuthenticatedAccount`, and `revoke` own server-session creation, hashing, expiry and auth-version checks, and current-token revocation. Only a token hash is stored in the database. |
| `boundary/auth/logout_page.py` | `post()` calls `logout() -> None`. The event asks the controller to revoke the current token, clears the browser session, and invokes `displayLoginPage() -> None`. Logout remains an authenticated POST. |
| `control/auth/logout_controller.py` | `logout(token) -> None` forwards revocation to `LoginSession.revoke`; it contains no SQL or browser-session changes. The report leaves the logout controller/entity boxes unnamed; these supporting classes preserve server-side logout. |
| `infrastructure/auth.py` | The framework adapter delegates authentication lookup to `LoginSession.getAuthenticatedAccount`, sets request globals, and clears invalid browser sessions. It also retains the safe internal redirect helper. |
| `templates/auth/login.html`, `templates/base.html`, `app.py` | Login and logout use plain HTML forms with generated CSRF tokens. Global `CSRFProtect` remains enabled. The unused `boundary/forms.py` module was removed. |

The UML event/display methods remain void. They set `self.rendered_page`; Flask's `get()` and `post()` adapters return the resulting HTTP response.

## Preserved rules

- Username and password are required, including rejection of whitespace-only fields. Maximum lengths remain 80 and 128 characters. Only the username is trimmed; password whitespace remains significant. Credential-setting password rules and hashing are unchanged.
- Login requires an active User Admin account and an active assigned profile. Incorrect credentials, unavailable accounts, and other roles retain the generic `Invalid login details` message.
- Failed attempts are grouped by request address and normalized username. The default remains five attempts within 15 minutes, configurable through `LOGIN_ATTEMPT_LIMIT`. Successful login clears failures for that key.
- Tokens are random, only their SHA-256 hashes are persisted, and expiry uses the configured session lifetime (30 minutes by default). Authentication-version changes invalidate earlier sessions.
- Logging in again rotates the current browser's token. Logging out revokes only the current token. Other browser sessions remain active.
- Login and logout remain protected by global CSRF validation. Cookie settings, safe internal redirects, database columns, and indexes are unchanged.

## Verification

Authentication regression tests exercise malformed inputs before database access, true/false login results, void boundary events, password whitespace, failure limits and clearing, the exact 15-minute cutoff, token hashing and rotation, configurable expiry, auth-version/status enforcement, safe redirects, CSRF rejection, and logout replay rejection while another browser stays signed in. Run `.venv/bin/python -m pytest tests/profiles -q` for the complete suite.
