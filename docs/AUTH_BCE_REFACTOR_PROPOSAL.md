# Login and logout BCE implementation

Login follows the report's classes and method names. Input cleanup and field validation belong to the boundary; the controller relays; the entity compares the submitted credentials with stored account data. The classroom demonstration uses a basic Flask browser session to display who is signed in.

| Class / method | Responsibility |
| --- | --- |
| `LoginPage.post()` | Read username/password from the HTML form and call the event method. |
| `LoginPage.clickLogin(username, password) -> None` | Validate required fields and lengths through `boundary.validation.validate_login_credentials`, trim the username, call the controller, then choose success or error display. Password whitespace is preserved. |
| `LoginPage.displayDashboard() -> None` | Prepare a dashboard redirect after storing the account ID in the browser session. |
| `LoginPage.displayError() -> None` | Show field or credential errors, retain the username, and leave the password blank. |
| `LoginController.login(username, password) -> bool` | Forward to `UserAccount().login` and relay the Boolean result, error message, and matched account. No SQL or input validation. |
| `UserAccount.login(username, password) -> bool` | Look up the account, compare the existing password hash, and check the stored account/profile status and User Admin role. |
| `LogoutPage.logout() -> None` | Clear the browser session and invoke `displayLoginPage`. |
| `LogoutPage.displayLoginPage() -> None` | Prepare a login redirect. |

The report does not name any logout controller/entity methods. The extra logout controller and server-session models were removed. The diagram's event/display methods remain void: they assign `self.rendered_page`, and Flask's `get()`/`post()` adapters return that HTTP response.

Login/logout remain demonstrable while the rest of the website can be used without signing in. Forms do not require CSRF tokens. Rate limiting, permission gates, server-side login tokens, token expiry/revocation, auth-version enforcement, custom security headers, and final-admin lockout rules were removed as approved for the classroom demo. Permission choices remain profile data.

Admin-created accounts remain password-free. The trusted bootstrap/reset commands can configure a password for demonstrating login. Existing password hashes and stored profile/account records are preserved; the basic Flask session still uses the configured SECRET_KEY. Old authentication tables are not dropped, and the unused auth_version column is retained for existing database compatibility.

See [the complete BCE map](STORIES_1_12.md) and [the implemented demo scope](BCE_DEMO_SIMPLIFICATION.md). Run `.venv/bin/python -m pytest tests/profiles -q` to verify input validation, duplicates, saved-data rules, numeric IDs, and basic login/logout.
