# Login and logout BCE implementation

Login follows the report's classes and method names. The boundary strips the username; the controller relays; the entity validates input and compares credentials with stored account data. The classroom demonstration uses a basic Flask browser session to display who is signed in.

| Class / method | Responsibility |
| --- | --- |
| `UserAdminLoginPage.post()` | Read username/password from the HTML form and call the event method. |
| `UserAdminLoginPage.onLogin(username, password) -> None` | Trim the username, call the controller, then choose success or error display using entity errors. Password whitespace is preserved. |
| `UserAdminLoginPage.displayDashboard() -> None` | Prepare a dashboard redirect after storing the account ID in the browser session. |
| `UserAdminLoginPage.displayError() -> None` | Show field or credential errors, retain the username, and leave the password blank. |
| `UserAdminLoginController.login(username, password) -> bool` | Forward to `UserAccount().login` and return the Boolean result; expose the operation entity for errors and the matched account. No SQL or input validation. |
| `UserAccount.login(username, password) -> bool` | Validate required fields and lengths, look up the account, compare the existing password hash, and check the stored account/profile status and User Admin role. |
| `LogoutPage.logout() -> None` | Clear the browser session and invoke `displayLoginPage`. |
| `LogoutPage.displayLoginPage() -> None` | Prepare a login redirect. |

The report does not name any logout controller/entity methods. The extra logout controller and server-session models were removed. The diagram's event/display methods remain void: they assign `self.rendered_page`, and Flask's `get()`/`post()` adapters return that HTTP response.

Pages require the matching active portal login. The latest remarks also add session-based account context and designer ownership checks; see [the review changes](BCE_REVIEW_CHANGES.md). Forms do not require CSRF tokens. Rate limiting, permission gates, server-side login tokens, token expiry/revocation, auth-version enforcement, custom security headers, and final-admin lockout rules were removed as approved for the classroom demo. Permission choices remain profile data.

Admin-created accounts start with the default password `password`, stored as a hash. Trusted bootstrap/reset commands can supply a different private password. Existing password hashes and stored profile/account records are preserved; the basic Flask session still uses the configured SECRET_KEY. Old authentication tables are not dropped, and the unused auth_version column is retained for existing database compatibility.

See [the complete BCE map](STORIES_1_12.md) and [the implemented demo scope](BCE_DEMO_SIMPLIFICATION.md). Run `.venv/bin/python -m pytest tests/sprint_1 tests/sprint_2 -q` for the current profile/account tests and basic User Admin login/logout. See [the test guide](TESTING_GUIDE.md) for the simplified scope.
