# BCE validation correction — 10 November 2026

Reviewed against `Nothinghere/CSIT314 Group Project Report (6).docx`, including all 48 BCE diagrams and the TDD statement that validation moved into entities. This correction replaces the earlier, incorrect 10 November boundary-validation guidance. See [the complete story/method audit](BCE_AUDIT_1_48.md).

| Layer | Responsibility |
| --- | --- |
| Boundary | Receive and strip ordinary input, call the controller, and display results/errors. Preserve passwords exactly. |
| Controller | Relay calls/results through its entity object. No input checks, SQL or copied error state. |
| Entity | Validate all fields, IDs, searches, dates and credentials, plus duplicates, references, assignments and saved state; perform database operations. |

`boundary/validation.py` contains only `strip_input`. Shared field rules now live in `entity/validation.py` and are called by entity operations. The unused infrastructure copy was removed. Invalid values reach the real controller and are rejected by the entity before records are changed; the boundary renders the returned field errors.

All affected profile/account, company/project, login, category, shortlist, search, detail/count and report pages follow this split. Existing tests that blocked controller calls were updated to exercise the real BCE path, checking errors and unchanged records. The suite retains exactly TC01–TC65.

The 48 diagrams are unchanged from the previous version: all 208 method entries retain their class/method names, parameter order/types and return types. Event/display methods remain void. Two necessary story-controller helpers are documented: the requested update-profile prefill getter and `ViewUserProfileController.listUserProfiles` for initial directories/dropdowns. A separate list operation lets the entity reject a submitted blank profile search without breaking the initial list. Staff selector checks also run in the account entity through a small relay controller.

Word (6) resolves the old report-test conflict. TC63–TC65 now check new projects, shortlist saves and top category. The fixtures match its exact dates and totals. Monthly reports validate the submitted start/end period in the entity, including reversed dates; a full calendar month remains the form default rather than an extra requirement.

Existing role/session/ownership behavior, the password-free account form and hashed default password `password` remain. No database columns, constraints or relationships changed; this correction needs no migration or data reset. The Word file was not edited. Remaining inconsistencies in its prose are listed in [the audit](BCE_AUDIT_1_48.md#document-conflicts-and-agreed-choices).

Verification: all 65 sprint tests pass on SQLite and PostgreSQL in disposable databases/isolated schemas. The 48-story/208-method contract check and 42-page HTML smoke checks pass. Existing ActivityEvent recording and report history are preserved. Restart Flask to load the changes.
