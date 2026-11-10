# Sprint test case map

Source: `Nothinghere/CSIT314 Group Project Report (6).docx`, Sprint 1, each story's **Test Case and Test Data → Checks** list. There are exactly 22 Sprint 1 test functions, with the document's case numbers in their names. Compound checks use one test function with multiple assertions rather than generating extra test cases.

| Case | Story | Document check covered |
| --- | ---: | --- |
| TC01 | 1 | Create form and required fields render, permissions are checkboxes, and incomplete submission saves nothing. |
| TC02 | 1 | Valid submission saves profile fields and selected permissions, displays success, and lists the profile. |
| TC03 | 1 | Duplicate profile names are rejected regardless of capitalization. |
| TC04 | 1 | Each missing required creation field causes an error and no profile is created. |
| TC05 | 1 | Unknown statuses are rejected. |
| TC06 | 1 | Names above 100 characters and descriptions above 10,000 characters are rejected. |
| TC07 | 1 | A profile can be created without permissions. |
| TC08 | 2 | The profile list displays active and suspended profiles with statuses. |
| TC09 | 2 | The selected profile's name, description, status, and permissions display correctly. |
| TC10 | 2 | Viewing a nonexistent profile returns an error. |
| TC11 | 2 | Profiles are listed alphabetically. |
| TC12 | 3 | The update form displays the existing name, description, and selected permissions. |
| TC13 | 3 | Updated fields and permissions are saved accurately and success displays. |
| TC14 | 3 | Renaming to another profile's name fails and the original record remains unchanged. |
| TC15 | 3 | Missing required update fields are rejected and saved values remain unchanged. |
| TC16 | 3 | Loading or submitting an update for a nonexistent profile returns an error. |
| TC17 | 4 | An unassigned profile can be suspended, with status saved and success displayed. |
| TC18 | 4 | An assigned profile cannot be suspended and remains active. |
| TC19 | 5 | Name searches work regardless of capitalization. |
| TC20 | 5 | Searching existing profile data returns the matching profile; this case searches its description. |
| TC21 | 5 | An unmatched search displays “No profiles found.” |
| TC22 | 5 | Empty or whitespace-only search displays a validation message. |

Story 3's ID heading says TC12–TC18, while its Checks list contains TC12–TC16. The tests follow the actual Checks list; Story 4 owns TC17–TC18. The document's T04–T07 spelling is normalized to TC04–TC07. TC08 and TC09 are included to match the updated document.

For Sprints 2–5, each story has one independent workflow test named `test_TCXX_description`, numbered consecutively from TC23 to TC65 in user-story order. Sprint 1 keeps TC01–TC22. The corresponding case ranges are listed below.

| Sprint | Stories | Test cases | One test per story |
| --- | --- | --- | --- |
| 2 | 6–10 | TC23–TC27 | Create an account with a hashed default password and verify login; view; update; suspend; search. |
| 2 | 11–12 | TC28–TC29 | User Admin login; logout. |
| 2 | 13–17 | TC30–TC34 | Create a company profile; view; delete; update; search. |
| 3 | 18–19 | TC35–TC36 | Interior Designer login; logout. |
| 3 | 20–24 | TC37–TC41 | Create a new project; update; view; search; delete. |
| 3 | 25–29 | TC42–TC46 | Create a past project; view; update; search; delete. |
| 4 | 30–34 | TC47–TC51 | Search projects; view a project; save a shortlist entry; search saved projects; view a saved project. |
| 4 | 35–36 | TC52–TC53 | Customer login; logout. |
| 4 | 37–38 | TC54–TC55 | View a project's view count; view its shortlist count. |
| 5 | 39–40 | TC56–TC57 | Platform Manager login; logout. |
| 5 | 41–45 | TC58–TC62 | Create a category; view; update; delete; search. |
| 5 | 46–48 | TC63–TC65 | Generate daily, weekly and monthly reports, checking new IDPs, shortlist-save actions, top category, saved dates and snapshots against known activity. |

Total: **65 tests**, covering all **48 stories**. Every test gets a disposable database or isolated test schema. Run commands and report locations are in [TESTING_GUIDE.md](TESTING_GUIDE.md).

The latest BCE review keeps the same 65 test functions. Shared fixtures arrange signed-in users. Existing story cases also check entity-level validation and the requested logged-out, wrong-role, and forged-ownership behavior; see [BCE_REVIEW_CHANGES.md](BCE_REVIEW_CHANGES.md).

## Report cases (Stories 46–48)

Word (6) resolves the old report-test mismatch: its cases now check new IDPs, shortlist saves and top category, matching the flows/wireframes. The existing tests use the exact document dates and totals:

| Case | Period | New IDPs | Shortlist saves | Top category |
| --- | --- | ---: | ---: | --- |
| TC63 | 4 November 2026 | 2 | 2 | Bohemian Living room |
| TC64 | 1–7 June 2026 | 1 | 8 | Transitional Kitchen |
| TC65 | 1–30 June 2026 | 10 | 32 | Bohemian Kitchen |

Fixtures use real entity operations. The same three cases retain checks of Singapore boundaries, New versus Past projects, removed/re-saved shortlists, historical category changes/deletions, empty periods, ties, saved snapshots and older saved reports. Monthly date validation accepts a selected valid period and rejects reversed dates in the entity.

TC34 searches **Updated Studio** and TC47 searches **Updated Seaside Home**, as specified in Word (6). Each test arranges its own update prerequisite rather than depending on another test's data.

## Entity validation verification

The existing cases send missing, malformed, overlong or unsupported values through the real boundary/controller/entity path. Boundaries strip ordinary input; entities reject invalid fields and return errors before records change. Tests no longer mock controllers to require an early boundary rejection. Duplicate/reference/state checks still use isolated database operations. Password whitespace is preserved, and the suite remains exactly TC01–TC65.
