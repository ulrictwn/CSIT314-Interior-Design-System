# User Admin test cases — stories 1–12

Scope: the original five profile stories and seven additional account/authentication stories. Each `TC` ID identifies one scenario. Bracketed values in a report identify different inputs for that scenario. Fixtures create a new isolated database/schema for every test, so cases do not depend on another case running first. These are automated checks of the working implementation, not the report's old non-persistent preview assertions.

| ID | Action / input | Expected result |
| --- | --- | --- |
| TC01.1 | Open Create profile | Screen, POST form and CSRF field render |
| TC01.2 | Inspect required fields | Name, description and status each appear and are marked required |
| TC01.3 | Open permission dropdown | Checkbox choices render; GET creates no profile |
| TC01.4 | Submit with each required field missing | HTTP 400 and validation message; database execute/add/flush/commit are never invoked |
| TC02 | Submit a valid profile with surrounding spaces | Redirect; trimmed values and selected permissions persist |
| TC03 | Create an existing name with different capitalization | Error; only the original record remains |
| TC04 | Submit with name, description or status missing | Error; no record created (3 input variants) |
| TC05 | Submit unknown status or permission code | Error; no record created (2 variants) |
| TC06 | Submit a 101-character name or 10,001-character description | Error (2 variants) |
| TC07 | Create with no permissions selected | Profile persists with an empty list |
| TC10 | Open directory with active/suspended profiles | Both profiles and statuses display |
| TC11 | Open details containing script-like description | Correct permissions display; HTML is escaped |
| TC12 | View nonexistent profile | HTTP 404 |
| TC13 | List profiles inserted in reverse name order | Predictable ascending name order |
| TC14 | Open Update | Current name, description and checkbox selection render |
| TC15 | Save changed name, description and permissions | Changed data persists |
| TC16 | Rename to another profile's name with different capitalization | Error; original record unchanged |
| TC17 | Save Update with a missing required field | Error; record unchanged (3 variants) |
| TC18 | Open Update for nonexistent profile | HTTP 404 |
| TC19 | Update while retaining original name | Save succeeds without a false duplicate error |
| TC20 | Open Update and follow Cancel destination | Original record unchanged |
| TC21 | Suspend profile with no assignments | Status becomes Suspended |
| TC22 | Suspend profile assigned to Active/Suspended account in either supported account table | “This profile is in use.”; profile stays Active (4 variants) |
| TC23 | Change an assigned profile's status through Update | Same assignment guard blocks suspension; record unchanged |
| TC24 | Open suspension confirmation and follow Cancel | No suspension from GET or Cancel |
| TC25 | Open suspension page for missing profile | HTTP 404 |
| TC26 | Search name using different capitalization | Matching profile displays |
| TC27 | Search text within description | Matching profile displays |
| TC28 | Search for unmatched text | No profiles found message |
| TC29 | Submit empty/whitespace search | Prompt for search input (2 variants) |
| TC30 | Search literal percent/underscore | Only literal matches, not all SQL wildcard matches (2 variants) |
| TC31 | Submit SQL injection-like search text | Query remains data; unrelated profiles are not returned |
| TC32 | Search script-like text | Reflected search text is HTML escaped |
| TC33 | Access without an authenticated test actor | HTTP 403 |
| TC34 | Access each feature without its permission | HTTP 403 for each page (5 variants) |
| TC35 | Use an authenticated actor while preview is disabled | Granted View works; ungranted Create is denied |
| TC36 | Submit create/update/suspend without CSRF token | HTTP 400; existing record unchanged (3 variants) |
| TC37 | Submit create/update/suspend with a valid CSRF token but no permission | HTTP 403; record unchanged (3 variants) |
| TC38 | Call controller directly without authorization | AccessError, independent of boundary checks |
| TC39 | Upgrade four-column singular/plural legacy table, then repeat upgrade | Data/permissions preserved, Active status added, singular profile table retained alongside the new tables (2 variants) |
| TC40 | Upgrade table containing case-insensitive duplicate names | Upgrade stops; neither row deleted |
| TC41 | Upgrade unfamiliar profile schema | Upgrade stops; table retained |
| TC42 | Suspend with an existing account table lacking assignment mapping | Error; profile remains Active |
| TC43 | Inspect permission column and reload stored values | PostgreSQL ARRAY / SQLite JSON as appropriate; list round-trips |
| TC44 | Request an unsupported directory operation | HTTP 400 |
| TC45 | Open profile search, then search Customer | All profiles initially; only matching rows after search |
| TC46 | Create each standard role's account | Active account with actual profile ID and shared account number: 202/302/402/102 after admin 101 (4 variants) |
| TC47 | Create two Customer accounts | Shared sequential account numbers; phone retained; account created without a usable password |
| TC48 | Create a case-insensitive duplicate username | Rejected; no extra account |
| TC49 | Omit each required account field | HTTP 400; no account created (5 variants) |
| TC50 | Assign a suspended profile on create | Rejected |
| TC51 | View account | Correct ID, username, name, email, phone, role and status; password absent |
| TC52 | View missing account | HTTP 404 |
| TC53 | Update permitted fields and submit forged username/status | Only name, email and profile change; ID/username/password/status remain |
| TC54 | Update with invalid email | Rejected; previous values retained |
| TC55 | Cancel Update | Navigation only; no stored change |
| TC56 | Reassign the final administrator to Customer | Rejected; admin access retained |
| TC57 | Suspend account twice | First persists Suspended without deleting; repeat rejected |
| TC58 | Suspend another signed-in admin | Its next protected request is denied |
| TC59 | Search ID, mixed-case username, full name, blank and whitespace | Correct matching rows; blank returns all (5 variants) |
| TC60 | Account search with no match | No accounts found message |
| TC61 | Valid active User Admin login | Redirect to working dashboard |
| TC62 | Bad password/username, non-admin, suspended account/profile | Same Invalid login details message; no protected access (5 variants) |
| TC63 | Enable legacy preview outside testing mode | Cannot bypass real login |
| TC64 | Repeated invalid credentials | Temporary throttle after five failures |
| TC65 | Logout and replay old cookie; keep another browser signed in | Current token revoked; old cookie denied; other browser works |
| TC66 | Logout through GET or missing CSRF | 405/400; valid session remains |
| TC67 | Remove each account permission | Corresponding account screen denied (5 variants) |
| TC68 | Create/update/suspend account without CSRF | 400; account data unchanged (3 variants) |
| TC69 | Rename, strip permission or suspend the last admin profile | Rejected; administrator role/access preserved (3 variants) |
| TC70 | Create accounts across several roles | IDs 101, 202, 303, 204, 105 share one account sequence |
| TC71 | Assign a custom profile with ID 12 | Account ID 1202 uses actual database profile ID |
| TC72 | Create after an existing UA101 account and legacy counter | Old account and counter retained; new customer gets 202 |
| TC73 | Generate a complete ID already occupied by another profile | Occupied ID skipped; existing account retained |
| TC74 | Account sequence passes 99 | Number expands without truncating or resetting |
| TC75 | Entity creation fails on duplicate email | Counter allocation rolls back; next valid account uses that number |
| TC76 | Create eight accounts concurrently across two roles | Eight unique complete IDs and distinct shared numbers 02–09 |
| TC77 | Open Create User Account | Username, full name, email, phone and profile fields render; password fields absent |
| TC78 | Create a User Admin without a password and try signing in | Account persists; login rejected until credentials are configured |
| TC79 | Inject password and confirm_password into the creation POST | Fields ignored; no credentials set |
| TC80 | Reassign the last usable admin while another admin has no password | Rejected; unconfigured account cannot substitute for a usable admin |
| TC81 | Set the new admin password through CLI, log in, then reassign the original admin | New admin signs in and remains authorized; old admin session loses access |

TC08 and TC09 are intentionally omitted. The combined HTML report has **125 individual results** on each database, including parameterized inputs and TC01 sub-checks. This is an automated regression suite, not a claim that every possible scenario is covered. Local SQLite verification passed; actual PostgreSQL verification is delegated to the supplied CI job. A skipped case is not a pass. Coverage measures executed lines separately.
