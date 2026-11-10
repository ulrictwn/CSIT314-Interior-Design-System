# Classroom BCE demonstration

The implementation follows the BCE classes/methods in `Nothinghere/CSIT314 Group Project Report (6).docx` and the latest lecturer remarks. The diagrams are unchanged from the previous report. Boundaries strip input and entities perform all validation, matching the report's TDD section. The [current review changes](BCE_REVIEW_CHANGES.md) and [48-story audit](BCE_AUDIT_1_48.md) define the latest validation split and required login preconditions.

| Layer | Responsibility |
| --- | --- |
| Boundary | Receive form/query/JSON values, strip ordinary text using only `strip_input` from `boundary/validation.py`, preserve passwords exactly, and display entity results/errors. |
| Control | Relay entity calls/results. Operation controllers retain `self.entity`; boundaries read its errors directly. |
| Entity | Validate all fields using `entity/validation.py`, including required values, formats, lengths, choices, IDs and searches; enforce duplicates, references and saved state; query/save data and allocate IDs. Trusted Python/CLI callers use the same checks. Assigned profiles cannot be suspended. |

Profile update follows the diagram's four arguments: `profileId, profileName, description, permissions`. The controller/entity keep `getUserProfile` for prefill. Update preserves status; Suspend changes it. Initial profile lists and dropdowns use the runtime helper `ViewUserProfileController.listUserProfiles` → `UserProfile.listUserProfiles`. The diagram's profile search method validates submitted text and rejects blank searches in the entity. Blank account searches still list all accounts. The extra list helper keeps these different required behaviors separate without adding a diagram argument.

Account creation needs no password entry and assigns the default password `password`, stored as a hash. IDs use the actual profile ID and shared sequence. Login validates credential fields and checks the existing password hash in `UserAccount.login`. The Staff selector uses the small `StaffLoginController.selectRole` relay to entity helper `UserAccount.staffRole`; the boundary displays an invalid choice or dispatches to the selected role's login event. The existing signed browser session identifies the account; logout clears it.

Pages now require the matching active portal role. Logged-out users go to the appropriate login page. Request-supplied account IDs cannot override the session. Designers can access only their own company and project operations; customer shortlist operations use the customer's own account.

The earlier removals of CSRF, login throttling, server-side session tokens/rotation/expiry/revocation, auth-version enforcement, custom security headers, and final-admin protection remain in effect. Profile permission choices remain stored data; the new access checks use portal roles and record ownership.

Existing model columns, records, passwords, and database credentials are preserved. Legacy authentication tables and the unused auth_version column remain untouched. No migration is needed for this refactor. The former `infrastructure/validation.py` module is removed; reusable validation is owned by `entity/validation.py`.
