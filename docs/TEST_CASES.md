# Profile test cases

Scope: the first five user stories. Each `TC` ID identifies one scenario. Bracketed values in a report identify different inputs for that scenario. Fixtures create a new isolated database/schema for every test, so cases do not depend on another case running first. These are automated checks of the working implementation, not the report's old non-persistent preview assertions.

| ID | Action / input | Expected result |
| --- | --- | --- |
| TC01 | Open Create profile | Required fields, CSRF field and permission checkboxes render |
| TC02 | Submit a valid profile with surrounding spaces | Redirect; trimmed values and selected permissions persist |
| TC03 | Create an existing name with different capitalization | Error; only the original record remains |
| TC04 | Submit with name, description or status missing | Error; no record created (3 input variants) |
| TC05 | Submit unknown status or permission code | Error; no record created (2 variants) |
| TC06 | Submit a 101-character name or 10,001-character description | Error (2 variants) |
| TC07 | Create with no permissions selected | Profile persists with an empty list |
| TC08 | Open Create then follow Cancel destination | Cancel is a navigation link; no record created |
| TC09 | Submit the same permission twice | Permission is stored once |
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
| TC33 | Access without authenticated actor or enabled preview | HTTP 403 |
| TC34 | Access each feature without its permission | HTTP 403 for each page (5 variants) |
| TC35 | Use an authenticated actor while preview is disabled | Granted View works; ungranted Create is denied |
| TC36 | Submit create/update/suspend without CSRF token | HTTP 400; existing record unchanged (3 variants) |
| TC37 | Submit create/update/suspend with a valid CSRF token but no permission | HTTP 403; record unchanged (3 variants) |
| TC38 | Call controller directly without authorization | AccessError, independent of boundary checks |
| TC39 | Upgrade four-column singular/plural legacy table, then repeat upgrade | Data/permissions preserved, Active status added, only singular profile table remains (2 variants) |
| TC40 | Upgrade table containing case-insensitive duplicate names | Upgrade stops; neither row deleted |
| TC41 | Upgrade unfamiliar profile schema | Upgrade stops; table retained |
| TC42 | Suspend with an existing account table lacking assignment mapping | Error; profile remains Active |
| TC43 | Inspect permission column and reload stored values | PostgreSQL ARRAY / SQLite JSON as appropriate; list round-trips |
| TC44 | Request an unsupported directory operation | HTTP 400 |

The HTML report and GitHub summary show **64 individual results** for these 44 scenarios on each database. The CI matrix therefore performs 128 test executions when both jobs finish. A green job check indicates overall job success; use the per-test rows/log for evidence of each scenario's actual outcome. Coverage HTML is a separate view of executed Python lines, not a test pass list.
