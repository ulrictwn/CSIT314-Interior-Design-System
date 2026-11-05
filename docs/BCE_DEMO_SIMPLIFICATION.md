# Classroom BCE demonstration

The implementation prioritizes the report's BCE classes, methods, and story flows.

| Layer | Responsibility |
| --- | --- |
| Boundary | Receive form/query values; trim input; validate required fields, lengths, formats, identifiers and supported choices; display results and errors. Shared plain functions live in `boundary/validation.py`. |
| Control | Relay boundary requests to entities and return results/error details. Controllers have no field validation, permission gates, or SQL. |
| Entity | Check duplicates, query/save database data, allocate account IDs, and apply rules based on saved records. Assigned profiles still cannot be suspended. |

Profile update now matches the diagram's four arguments: `profileId, profileName, description, permissions`. Its controller/entity retain `getUserProfile` for prefill as requested. Update preserves status; Suspend changes it.

Password-free admin account creation is retained as explicitly confirmed, along with numeric IDs based on the actual profile ID and shared account sequence. Login keeps the diagram's username/password flow and compares existing password hashes. Logout simply clears the basic browser session.

The approved simplification removed authorization/permission checks, CSRF protection and hidden tokens, login throttling and attempt records, server-side session tokens/rotation/expiry/revocation, auth-version enforcement, custom security headers, and final-admin protection. The corresponding unused base classes, logout controller, authentication models, settings, and dependencies were removed.

Profile/account database columns and stored records were preserved. The unused auth_version column remains for compatibility, and legacy authentication tables are left untouched and unused. Existing password hashes and database credentials were not rewritten. No database reset or migration is needed for these code changes.
