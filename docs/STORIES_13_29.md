# Stories 13–29: designer BCE implementation

Source: the BCE diagrams in `CSIT314 Group Project Report (4).docx`.

These stories have Python boundary, controller, and entity implementations, with HTML screens based on the references in `Nothinghere/`. The boundary display methods render HTML for browsers and retain JSON responses for API clients. The event/display method names and void signatures remain aligned with the diagrams. The existing Stories 1–12 HTML remains in place.

## Files and diagram classes

| Story | Boundary file / class | Controller | Entity operation |
| --- | --- | --- | --- |
| 13 | `boundary/company/create_company_profile_page.py` — `CreateCompanyProfilePage` | `CreateCompanyProfileController` | `CompanyProfile.createCompanyProfile` |
| 14 | `boundary/company/view_company_profile_page.py` — `ViewCompanyProfilePage` | `ViewCompanyProfileController` | `CompanyProfile.getCompanyProfile` |
| 15 | `boundary/company/delete_company_profile_page.py` — `DeleteCompanyProfilePage` | `DeleteCompanyProfileController` | `CompanyProfile.deleteCompanyProfile` |
| 16 | `boundary/company/update_company_profile_page.py` — `UpdateCompanyProfilePage` | `UpdateCompanyProfileController` | `CompanyProfile.updateCompanyProfile` |
| 17 | `boundary/company/search_company_profile_page.py` — `SearchCompanyProfilePage` | `SearchCompanyProfileController` | `CompanyProfile.searchCompanyProfile` |
| 18 | `boundary/designer/interior_designer_login_page.py` — `InteriorDesignerLoginPage` | `InteriorDesignerLoginController` | `UserAccount.login` |
| 19 | `boundary/designer/interior_designer_logout_page.py` — `InteriorDesignerLogoutPage` | The diagram has no named control methods | The diagram has no named entity methods |
| 20 | `boundary/projects/create_new_project_page.py` — `CreateNewProjectPage` | `CreateNewProjectController` | `InteriorDesignProject.createNewProject` |
| 21 | `boundary/projects/update_new_project_page.py` — `UpdateNewProjectPage` | `UpdateNewProjectController` | `InteriorDesignProject.updateNewProject` |
| 22 | `boundary/projects/view_new_project_page.py` — `ViewNewProjectPage` | `ViewNewProjectController` | `InteriorDesignProject.getNewProject` |
| 23 | `boundary/projects/search_new_project_page.py` — `SearchNewProjectPage` | `SearchNewProjectController` | `InteriorDesignProject.searchNewProjects` |
| 24 | `boundary/projects/delete_new_project_page.py` — `DeleteNewProjectPage` | `DeleteNewProjectController` | `InteriorDesignProject.deleteNewProject` |
| 25 | `boundary/projects/create_past_project_page.py` — `CreatePastProjectPage` | `CreatePastProjectController` | `InteriorDesignProject.createPastProject` |
| 26 | `boundary/projects/view_past_project_page.py` — `ViewPastProjectPage` | `ViewPastProjectController` | `InteriorDesignProject.getPastProject` |
| 27 | `boundary/projects/update_past_project_page.py` — `UpdatePastProjectPage` | `UpdatePastProjectController` | `InteriorDesignProject.updatePastProject` |
| 28 | `boundary/projects/search_past_project_page.py` — `SearchPastProjectPage` | `SearchPastProjectController` | `InteriorDesignProject.searchPastProjects` |
| 29 | `boundary/projects/delete_past_project_page.py` — `DeletePastProjectPage` | `DeletePastProjectController` | `InteriorDesignProject.deletePastProject` |

Controller files live under the matching `control/company/`, `control/designer/`, and `control/projects/` folders. Persistence lives in `entity/company/company_profile.py` and `entity/projects/interior_design_project.py`. Designer login reuses `entity/accounts/user_account.py`, as the diagram specifies; no duplicate account entity was introduced.

## Responsibilities

Boundaries own `.strip()`, required-field/type/length checks, email/phone format checks, positive identifiers, and finite non-negative renovation costs. Shared field checks are in `boundary/company/validation.py`, `boundary/projects/validation.py`, and the existing `boundary/validation.py`. Controllers only relay calls and results. Entities handle duplicate checks, existing-account/record checks, phase-specific queries and writes, and database transactions.

The public event and display methods keep `-> None` (UML void). They assign `self.rendered_page`; Flask's HTTP adapters return it. Mutation controller/entity methods return `bool`. Getter methods return an entity or `None` when no matching record exists.

Update/delete controllers include getters for prefill and confirmation. GET requests return existing values without modifying data; POST invokes the diagram event. The additional getters support the normal flows described in the report.

### Company profiles

The create/update fields are `companyName`, `companyContact`, `companyAddress`, `companyEmail`, and `companyRegistrationNumber`. The account ID comes from boundary context rather than an extra event argument, matching the diagrams.

A company profile is keyed by account ID because the diagram's getter/update/delete operations identify it that way. Entities reject an existing profile for the same account and case-insensitive duplicate business registration numbers. Input limits are name 150, contact 40, address 1000, email 254, and registration number 100 characters.

`searchCompanyProfile(accountId, keyword)` returns `list[str]`, as specified by the BCE diagram: matching labelled field values from that account's profile. A blank search returns all five company fields. Missing/no-match data returns an empty list.

### New and past projects

The diagram fields are `projectName`, `categoryId`, `propertyType`, `area`, `renovationCost`, and `description`. Area remains a string so values such as `120 sqm` can be stored. Input limits are name 150, property type/area 100, and description 10000 characters. IDs are positive database integers, and renovation cost is a finite number of zero or more.

One `InteriorDesignProject` model stores both types using `project_status` (`New` or `Past`). Each type has the diagram's separate create/get/update/search/delete methods. Queries and writes cannot operate on the other project type accidentally. Searches are scoped by account ID, with case-insensitive literal substring matching; blank searches list that account's projects of the requested type.

Names are unique per account and project type, including case-insensitive duplicates. Another account or the other project type can reuse a name. Project IDs are generated by the database. Updating preserves the owner, ID, and project type. Creating a past project creates its own record from the six diagram fields; there is no unlisted conversion argument.

Category lookup was deferred during Stories 13–29 and is now connected through Stories 41–45. `categoryId` must reference a saved category, and the project form provides a category selector. See [the Sprint 4–5 notes](SPRINTS_4_5_IMPLEMENTATION.md).

### Designer login/logout

`InteriorDesignerLoginPage.onLogin(username, password)` validates the input and calls `InteriorDesignerLoginController.login`. The entity receives `profileName='Interior Designer'` and checks the stored password hash and account/profile status and role. The existing admin login still defaults to `User Admin`.

Successful login stores only the account ID in the existing basic browser session. Logout clears it and redirects to the designer login endpoint. No permission gates, CSRF, rate limits, or server-session security were added. Explicit account IDs can be supplied to exercise the data flows without signing in.

## HTML/JSON routes and account context

The request adapters are registered in `boundary/designer/routes.py`. They accept form data or JSON using the camelCase field names above. Browsers receive HTML through their `Accept: text/html` header. API clients can request `Accept: application/json` or `?format=json`; JSON request bodies always retain JSON responses. Requests with no Accept header retain the original JSON interface. `?format=html` is also available for manual previews.

Account context comes from an explicit boundary constructor argument, request `accountId`, or the existing browser session. HTML links and forms carry an explicit account ID when supplied. This supplies the owner relationship; it does not enforce authorization.

| Routes | Behavior |
| --- | --- |
| `/designer/login` | GET designer sign-in / JSON field metadata; POST designer login |
| `/designer/logout` | POST logout |
| `/designer` | Designer dashboard / JSON links and current account ID |
| `/designer/company/create` | GET form / fields; POST create |
| `/designer/company` | GET own company profile |
| `/designer/company/update` | GET prefill; POST update |
| `/designer/company/delete` | GET confirmation data; POST delete |
| `/designer/company/search?q=...` | GET/POST company-field search |
| `/designer/projects/new` and `/designer/projects/past` | GET own projects of that type |
| `/designer/projects/{type}/create` | GET form / fields; POST create |
| `/designer/projects/{type}/search?q=...` | GET/POST project-name search |
| `/designer/projects/{type}/{projectId}` | GET project details |
| `/designer/projects/{type}/{projectId}/update` | GET prefill; POST update |
| `/designer/projects/{type}/{projectId}/delete` | GET confirmation data; POST delete |

Replace `{type}` with `new` or `past`. JSON create responses use 201, reads/updates/deletes use 200, invalid fields/duplicates use 400, and missing records use 404. Successful HTML mutations redirect with 303 to a detail or collection page and show a success message. Invalid HTML submissions redisplay entered values and errors. Basic login/logout redirect to the designer dashboard/login endpoint. Owner-dependent calls without an account ID return a field/context error with a way to enter an account ID.

Project collections accept `mode=view`, `mode=search`, `mode=update`, or `mode=delete` to select the row action. Sidebar Search links open the list directly. Delete GETs show confirmation and Cancel; only POST deletes a record. Blank searches show all relevant records.

`templates/auth/login.html` provides the Staff/Customer slider. Staff submits through `/staff/login`, which dispatches to the Admin, Interior Designer, or Platform Manager BCE boundary. Company templates live in `templates/company/`; project templates live in `templates/projects/`; designer layout/dashboard and shared macros live in `templates/designer/`. Shared HTML presentation is in `boundary/designer/presentation.py`; no controller/entity rendering was introduced. See [the frontend notes](FRONTEND_IMPLEMENTATION.md) for the reference scope and image asset.

For example, POST `/designer/projects/new/create?accountId=YOUR_ACCOUNT_ID` with:

```json
{
  "projectName": "Seaside Home",
  "categoryId": 1,
  "propertyType": "Apartment",
  "area": "120 sqm",
  "renovationCost": 80000.5,
  "description": "A bright renovation project."
}
```

Use an existing account ID. The `?accountId=...` can be omitted after a successful designer login.

## Database setup and verification

Run the existing additive setup command against the intended development database before exercising the new persistence:

```bash
.venv/bin/python -m flask --app app upgrade-db
```

It registers/creates the `company_profile` and `interior_design_project` tables. Existing profile/account columns, account IDs, and password hashes are preserved; no database reset is required. This implementation was verified against disposable test databases rather than resetting the application's database.

Tests are grouped into `tests/company/`, `tests/designer/`, `tests/projects/`, and the existing `tests/profiles/`, with shared fixtures in `tests/conftest.py`. All seventeen diagram class/event/operation signatures are checked, alongside validation before controller calls, duplicate rollback, owner/type separation, prefill, deletion confirmation, login/logout, category deferral, and additive database setup.

```bash
.venv/bin/python -m pytest tests -q
```

The existing CI/report command `python scripts/run_profile_tests.py` now includes all test folders and Stories 1–48.
