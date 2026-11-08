# BCE review changes — 8 November 2026

These changes apply the latest lecturer feedback to Stories 1–48. They supersede the earlier boundary-validation and public-page demo requirements. The 207 methods transcribed from the BCE diagrams keep their names, parameter lists, annotations, and return types. Event/display methods remain void.

## Layer responsibilities

| Layer | Responsibility |
| --- | --- |
| Boundary | Receive form/query/JSON input, strip ordinary text, call the controller, and prepare displays, messages, redirects, or JSON. Passwords are never stripped. |
| Controller | Retain an entity operation object and relay the method call and result. No validation, SQL, or copying of entity errors. |
| Entity | Validate required fields, supported choices, lengths, formats, numeric/date values, duplicates, references, and saved state; query and persist data. |

`boundary/validation.py` now contains only `strip_input`. Shared field checks are in `entity/validation.py`, with company/project/category/report helpers under their matching entity folders. Entity operations invoke those validators themselves, so direct calls also reject invalid fields. Boundary feature helpers named `presentation.py` contain form field names, serialization, and display defaults.

For example, the profile controller now contains:

```python
class CreateUserProfileController:
    def __init__(self):
        self.entity = UserProfile()

    def createUserProfile(self, profileName: str, description: str,
                          status: str, permissions: list[str]) -> bool:
        return self.entity.createUserProfile(profileName, description, status, permissions)
```

On failure, the boundary reads `controller.entity.error_message`, `field_errors`, and (where needed) `error_reason`. Login pages read the matched account from `controller.entity.authenticated_account`. Display-only permission options remain in the boundary; the unused controller alias was removed.

`activeProfiles()` now belongs to `UserProfile`. The account create/update controllers relay to `UserProfile.activeProfiles()` to populate their dropdowns.

## Portal access

| Signed-in profile | Pages |
| --- | --- |
| User Admin | Profile and account administration |
| Interior Designer | Own company, new/past projects, and interest counts |
| Customer | Project discovery and own shortlist |
| Platform Manager / Platform Management | Category management and activity reports |

`infrastructure/auth.py` loads the existing browser session and checks the saved active account/profile on protected requests. Missing login redirects to that portal's login page; a different role receives HTTP 403. Login selectors and static files remain public.

The session selects the account. A request cannot switch the actor by supplying a different `accountId` in a query, form, or JSON body. Designer project IDs are also checked for ownership before viewing, updating, deleting, or reading interest counts. Customers can view published project details across designers, while shortlist operations use the customer's own account.

These are the requested basic login, role, and ownership checks. CSRF, rate limiting, server-side session tokens, and final-admin protection remain outside the classroom scope.

## Verification and setup

The sprint suite retains 65 test functions: TC01–TC22 for Sprint 1 and one test per later story. Fixtures now arrange a signed-in actor for the relevant portal. Existing story cases also check direct entity rejection, missing login, wrong roles, forged company account IDs, and other designers' project IDs. All 65 tests passed on SQLite and PostgreSQL. HTML smoke checks covered all four portals, validation messages, shortlist saving, report generation/download, and logout redirects. See [the test guide](TESTING_GUIDE.md).

No model columns or table definitions changed, so this refactor requires no database migration. Restart Flask to load the changed modules. Admin-created accounts remain password-free; the existing trusted `reset-password` command configures an account for sign-in.
