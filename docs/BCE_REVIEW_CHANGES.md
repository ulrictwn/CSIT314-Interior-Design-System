# BCE validation and cleanup — 10 November 2026

The current audit covers all 48 stories in Word version (5). This update supersedes the earlier rule that boundaries only strip input. See [the complete story/method audit](BCE_AUDIT_1_48.md).

| Layer | Responsibility |
| --- | --- |
| Boundary | Receive and strip ordinary input; reject missing, malformed, overlong or unsupported field values before the controller; display results. Preserve passwords exactly. |
| Controller | Relay calls/results through its entity object. No input checks, SQL or copied error state. |
| Entity | Validate duplicates, references, assignments, membership and stored state; perform database operations. Essential shared value checks also protect direct/CLI callers. |

Boundary events call the checks exposed by `boundary/validation.py`. Their single pure implementation is in `infrastructure/validation.py`, which has no database, entity-model or Flask dependencies. The five entity validation helper modules have been consolidated into that file.

Profile/account lists and active-profile dropdowns reuse existing diagram Search operations, so the separate Directory controllers and entity list helpers were removed. The assignment check lives directly in `UserProfile.suspendUserProfile`. Staff role-selector input is checked in the Staff boundary; the selector-only controller/entity method were removed. Error rendering for report generation and account suspension is inside the diagram events. Unused auth re-exports and persistence wrappers were removed.

The requested `UpdateUserProfileController.getUserProfile` prefill method remains. Flask adapters, constructors, required setup/password/serialization support, report activity history, stored-report reads/downloads, the supplied remove-shortlist wireframe and dashboards still serve required behavior. No speculative fields or features were added.

Existing role/session/ownership checks remain to enforce the document's login preconditions and scoped-account tests. CSRF, throttling, server-side session tokens and final-admin protection remain outside the demo scope. Account creation retains the password-free form and hashed default password `password`.

All 208 diagram method entries retain their names, parameter order/types and return types; event/display methods remain void. All 65 sprint tests pass on SQLite and PostgreSQL. Existing tests assert that invalid fields do not reach action controllers. The table schema and stored records need no changes; restart Flask.

The subsequent method simplification removes all six `_reject` helpers and the private New/Past CRUD, duplicate-query and keyword helpers. Error handling and database work now live directly in the diagram operations. All 409 application methods/functions have short explanations; local imports name their source files. Diagram signatures and runtime behavior remain unchanged.
