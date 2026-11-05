# Classroom demonstration test cases

Fixtures create an isolated SQLite database or dedicated PostgreSQL schema for every test. Application records and `.env` credentials are not used. The current count and parameterized results are reported by pytest and the CI HTML report.

| Area | Expected behavior |
| --- | --- |
| Create profile | Boundary trims fields and validates required fields, lengths, Boolean status and permission choices; entity rejects duplicate names and persists valid data. |
| View profile | Boundary rejects malformed identifiers; entity returns the matching record or no record; details render safely. |
| Update profile | Saved values load before editing. Four diagram arguments update name/description/permissions, preserving status. Duplicate names fail without changing the record. |
| Suspend profile | Unassigned profiles are suspended; profiles assigned to active or suspended accounts remain unchanged. |
| Search profiles | Initial page lists all profiles. Boundary requires nonblank submitted text and validates length; entity searches saved data. |
| Create account | Boundary validates and trims username/name/email/phone/profile ID; entity checks duplicate username/email and active profile assignment. Web creation remains password-free. |
| Numeric IDs | Actual profile IDs and a shared counter produce stable IDs, handle collisions, preserve legacy IDs, and roll back allocation after failure. |
| View/update account | Saved data displays before editing. Boundary validates input. Entity rejects duplicate email and preserves fields outside the diagram's arguments. |
| Suspend account | Status changes without deleting account data; repeated suspension returns the existing error. Final-admin lockout protection is not part of the demo. |
| Search accounts | Boundary normalizes/validates the keyword; blank lists all accounts. |
| Login | Boundary rejects malformed fields before controller access, trims only the username, and preserves password whitespace. Entity matches saved credentials and stored account/profile status and role. Invalid attempts are not rate limited. |
| Logout | Current browser login is cleared and login page is displayed; another browser's login remains unchanged. |
| Public demo flows | Pages and valid POST operations work without authorization or CSRF tokens. Input validation still rejects incorrect data. |
| Persistence | Duplicate failures leave the database usable, schema upgrades preserve existing records, and unsupported schemas stop without deleting data. |

The former tests for permission gates, CSRF, throttling, server-token replay rejection, and final-admin protection were replaced with tests of the explicitly approved classroom behavior. Input-validation tests now assert that rejection occurs at the boundary; duplicate and database tests still exercise entities directly.
