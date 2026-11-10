# Classroom BCE demonstration

The implementation follows the report's BCE classes/methods and the latest lecturer remarks. The [current review changes](BCE_REVIEW_CHANGES.md) and [48-story audit](BCE_AUDIT_1_48.md) define the latest validation split and required login preconditions.

| Layer | Responsibility |
| --- | --- |
| Boundary | Receive form/query/JSON values, strip ordinary text, validate required/incorrect fields before controllers, and display results/errors. `boundary/validation.py` exposes shared pure checks. Password whitespace is preserved. |
| Control | Relay entity calls/results. Operation controllers retain `self.entity`; boundaries read its errors directly. |
| Entity | Validate duplicates, references and saved state; query/save data and allocate IDs. Reuse essential value checks for direct Python/CLI calls. Assigned profiles cannot be suspended. |

Profile update follows the diagram's four arguments: `profileId, profileName, description, permissions`. The controller/entity keep `getUserProfile` for prefill. Update preserves status; Suspend changes it. The diagram search methods supply profile/account lists and dropdowns; separate directory/list helpers were removed.

Account creation needs no password entry and assigns the default password `password`, stored as a hash. IDs use the actual profile ID and shared sequence. Login checks the existing password hash. The existing signed browser session identifies the account; logout clears it.

Pages now require the matching active portal role. Logged-out users go to the appropriate login page. Request-supplied account IDs cannot override the session. Designers can access only their own company and project operations; customer shortlist operations use the customer's own account.

The earlier removals of CSRF, login throttling, server-side session tokens/rotation/expiry/revocation, auth-version enforcement, custom security headers, and final-admin protection remain in effect. Profile permission choices remain stored data; the new access checks use portal roles and record ownership.

Existing model columns, records, passwords, and database credentials are preserved. Legacy authentication tables and the unused auth_version column remain untouched. No migration is needed for this refactor.
