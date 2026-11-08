# Sprint test case map

Source: `Nothinghere/CSIT314 Group Project Report (4).docx`, Sprint 1, each story's **Test Case and Test Data → Checks** list. There are exactly 22 Sprint 1 test functions, with the document's case numbers in their names. Compound checks use one test function with multiple assertions rather than generating extra test cases.

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

For Sprints 2–5, each story has one independent successful workflow test. These US labels identify the story; they are not additional Word-document TC numbers.

| Sprint | Stories | One test per story |
| --- | --- | --- |
| 2 | 6–10 | Create a password-free account; view; update; suspend; search. |
| 2 | 11–12 | User Admin login; logout. |
| 2 | 13–17 | Create a company profile; view; delete; update; search. |
| 3 | 18–19 | Interior Designer login; logout. |
| 3 | 20–24 | Create a new project; update; view; search; delete. |
| 3 | 25–29 | Create a past project; view; update; search; delete. |
| 4 | 30–34 | Search projects; view a project; save a shortlist entry; search saved projects; view a saved project. |
| 4 | 35–36 | Customer login; logout. |
| 4 | 37–38 | View a project's view count; view its shortlist count. |
| 5 | 39–40 | Platform Manager login; logout. |
| 5 | 41–45 | Create a category; view; update; delete; search. |
| 5 | 46–48 | Generate a daily report; weekly report; monthly report, checking saved dates and totals against known activity. |

Total: **65 tests**, covering all **48 stories**. Every test gets a disposable database or isolated test schema. Run commands and report locations are in [TESTING_GUIDE.md](TESTING_GUIDE.md).

The latest BCE review keeps the same 65 test functions. Shared fixtures arrange signed-in users. Existing story cases also check entity-level validation and the requested logged-out, wrong-role, and forged-ownership behavior; see [BCE_REVIEW_CHANGES.md](BCE_REVIEW_CHANGES.md).
