# Sprints 4 and 5 — Stories 30–48

The implementation uses the BCE diagrams in `Nothinghere/CSIT314 Group Project Report (5).docx` and the screenshots under `Nothinghere/Customer/` and `Nothinghere/Platform manager/`. Existing Stories 1–29 remain connected to the same application.

## Diagram map

| Story | Boundary class | Controller operation | Entity operation |
| --- | --- | --- | --- |
| 30 | `SearchIDPPage.onSearch(keyword)` | `SearchIDPController.search_all_IDPs(keyword)` | `InteriorDesignProject.search_all_IDPs(keyword)` |
| 31 | `ViewIDPPage.onView(projectId)` | `ViewIDPController.getIDP(projectId)` | `InteriorDesignProject.getIDP(projectId)` |
| 32 | `SaveShortlistIDPPage.onSave(projectId)` | `SaveShortlistIDPController.saveShortlist(accountId, projectId)` | `Shortlist.saveShortlist(accountId, projectId)` |
| 33 | `SearchShortlistIDPPage.onSearch(keyword)` | `SearchShortlistIDPController.search_shortlist_IDP(accountId, keyword)` | `InteriorDesignProject.search_shortlist_IDP(accountId, keyword)` |
| 34 | `ViewShortlistIDPPage.onView(projectId)` | `ViewShortlistIDPController.getIDP(projectId)` | `InteriorDesignProject.getIDP(projectId)` after checking the saved relationship |
| 35 | `CustomerLoginPage.onLogin(username, password)` | `CustomerLoginController.login(username, password)` | `UserAccount.login(username, password, profileName)` |
| 36 | `LogoutPage.logout()` in `boundary/customer/` | None specified | None specified |
| 37 | `ViewCountPage.onView(projectId)` | `ViewCountController.getViewCount(projectId)` | `InteriorDesignProject.getViewCount(projectId)` |
| 38 | `ViewShortlistCountPage.onView(projectId)` | `ViewShortlistCountController.getShortlistCount(projectId)` | `Shortlist.getShortlistCount(projectId)` |
| 39 | `PlatformManagerLoginPage.onLogin(username, password)` | `PlatformManagerLoginController.login(username, password)` | `UserAccount.login(username, password, profileName)` |
| 40 | `PlatformManagerLogoutPage.logout()` | None specified | None specified |
| 41 | `CreateCategoryPage.onCreate(categoryName, description)` | `CreateCategoryController.createCategory(...)` | `Category.createCategory(...)`, `categoryExists(categoryName)` |
| 42 | `ViewCategoryPage.onView(categoryId)` | `ViewCategoryController.getCategory(categoryId)` | `Category.getCategory(categoryId)` |
| 43 | `UpdateCategoryPage.onUpdate(categoryId, categoryName, description)` | `UpdateCategoryController.updateCategory(...)` | `Category.updateCategory(...)` |
| 44 | `DeleteCategoryPage.onDelete(categoryId)` | `DeleteCategoryController.deleteCategory(categoryId)` | `Category.deleteCategory(categoryId)` |
| 45 | `SearchCategoryPage.onSearch(keyword)` | `SearchCategoryController.searchCategories(keyword)` | `Category.searchCategories(keyword)` |
| 46 | `DailyReportPage.onGenerateDailyReport(startDate)` | `DailyReportController.generateDailyReport(startDate)` | `Report.generateReport(reportType, startDate, endDate)` |
| 47 | `WeeklyReportPage.onGenerateWeeklyReport(startDate)` | `WeeklyReportController.generateWeeklyReport(startDate)` | `Report.generateReport(reportType, startDate, endDate)` |
| 48 | `MonthlyReportPage.onGenerateMonthlyReport(startDate, endDate)` | `MonthlyReportController.generateMonthlyReport(startDate, endDate)` | `Report.generateReport(reportType, startDate, endDate)` |

The updated report (4) now includes the BCE diagrams for Stories 46–48. The classes, event names, displayReport(report) methods, and date parameters match those diagrams. Daily/weekly accept startDate; monthly accepts startDate and endDate. All three use the entity operation generateReport(reportType, startDate, endDate). See [the full 48-story audit](BCE_AUDIT_1_48.md).

All event and display methods retain `-> None` (UML void), assigning `self.rendered_page`. Flask `get`/`post` adapters return the resulting response. Controllers relay entity calls and results. Boundaries strip ordinary text and display entity results/errors. Entities validate fields, lengths, formats, identifiers, dates, references, duplicates, saved relationships, counts, and transactions.

## Folder layout

- `boundary/customer/` and `control/customer/`: discovery, shortlist, customer login/logout, dashboard.
- `boundary/categories/`, `control/categories/`, `entity/categories/`: category operations.
- `boundary/platform_manager/`, `control/platform_manager/`: manager login/logout and dashboard.
- `boundary/reports/`, `control/reports/`, `entity/reports/`: report pages, stored snapshots, activity data.
- `entity/shortlist/`: customer/project saved relationships.
- `boundary/designer/` and `control/designer/`: the additional view/shortlist count stories.
- `templates/customer/`, `templates/categories/`, `templates/platform_manager/`, `templates/reports/`, `templates/interest/`: corresponding HTML.
- `templates/portal/`, `boundary/portal.py`, `static/css/portals.css`, `static/js/portals.js`: shared portal presentation.

The root test-output directory `/reports/` is ignored by Git. The ignore rule is anchored so application source folders named `reports` are included in the repository.

## Login and dashboards

The animated selector now has **Staff** and **Customer** sides. Staff has a role selector for User Admin, Interior Designer, and Platform Manager. Its form submits to `StaffLoginPage`, which selects the role-specific boundary event; each event still calls its own controller and the existing account entity. The controls work with keyboard navigation, reduced motion, or JavaScript disabled.

| Role | Login | Dashboard | Logout (POST) |
| --- | --- | --- | --- |
| User Admin | `/login` or `/staff/login` | `/dashboard` | `/logout` |
| Interior Designer | `/designer/login` | `/designer` | `/designer/logout` |
| Customer | `/customer/login` | `/customer` | `/customer/logout` |
| Platform Manager | `/manager/login` | `/manager` | `/manager/logout` |

The existing `Platform Management` profile name and `Platform Manager` are both accepted by the manager login. Saved profile names and account IDs are preserved. Admin-created accounts start with the default password `password`. To choose a different private password, use the existing terminal command:

```bash
.venv/bin/python -m flask --app app reset-password --username YOUR_USERNAME
```

The latest remarks add login, portal-role, and ownership checks. Sessions supply account context; conflicting `accountId` values are rejected. CSRF, rate limiting, and server-side session tokens remain outside the demo scope. Existing passwords remain hashed. See [the current review changes](BCE_REVIEW_CHANGES.md).

## Customer and designer flows

Customers can browse both New and Past projects across designers. Search matches project name, ID (`IDP1`), category name, property type, area/location, or description. Blank searches show all relevant projects; `%` and `_` are literal characters. Shortlist searches are scoped to the supplied/current account.

A shortlist has a unique `(account_id, project_id)` key. Duplicate saves and missing accounts/projects are rejected by the entity. The saved relationship is checked before opening a shortlisted project. **Remove shortlist** is an extra boundary/controller/entity operation to support the supplied Story 34 screenshot. Removing a save keeps the project. Deleting a project removes its saved relationships through the database foreign key.

`getIDP(projectId)` calls `incrementViewCount(projectId)` as shown in Stories 31 and 34. Each successful customer detail-page request increments the count atomically. Searches, designer project reads, count pages, and report generation do not increment it. Shortlist counts show the number of customers currently saving a project. Designers can open the two Project Interest links in their sidebar.

Project photos were not added to the diagram model. Detail-page images remain captioned **Interior inspiration**; list rows use project icons.

## Categories

Category names are required, at most 100 characters, and unique ignoring case. Descriptions are required and at most 10,000 characters. Numeric category IDs remain stable; `CAT1` is their display label. Search includes name, description, and displayed ID. GET update/delete requests prefill/show confirmation; only POST writes.

Now that the later category stories exist, designer project forms select from saved categories. Entities reject nonexistent categories. A category used by projects cannot be deleted; assign those projects another category first. Projects are preserved.

## Reports

Daily reports cover one day, weekly reports seven consecutive days, and monthly reports a complete calendar month. The Report entity validates ISO date input (or date objects in direct BCE calls), supported years (1900–9998), and the selected interval. Daily/weekly end dates are read-only and derived from startDate; monthly accepts both dates. Changing the start date fills the corresponding end date in the browser. Date boundaries and generation labels use **Asia/Singapore**; event timestamps are stored in UTC.

Reports store an immutable snapshot for the selected period. CSV downloads read that snapshot, so later activity does not change an existing report. Generate another report to include new activity.

Stories 46–48 use their **Normal Flow** and the updated wireframes embedded in Word version (5). The three summary figures are **new IDPs created**, **times customers shortlisted a project**, and **top IDP category**. The wireframes define the top category as the category with the most new IDPs created in the selected period. Past projects added are excluded. Equal category counts use alphabetical name order (then category ID); an empty period has zero counts and no top category. The detail table and CSV show the new-IDP counts by category.

`ActivityEvent` supplies the dated creation and shortlist-save history. A removed shortlist still counts as a save action in its original period; saving it again counts again. Failed or duplicate saves add no event. Project creation events retain the creation-time category ID and name, so later reassignment or deletion does not erase their contribution. A surviving category uses its current label for new reports; a deleted category uses its recorded label. Existing saved report snapshots and CSV downloads keep their original values and remain readable, including older reports with login/registration metrics. Generate a new report to use the corrected format.

The Word document's **TC63–TC65 test descriptions still list login and registration totals**, contradicting the Normal Flow and updated wireframes. The three code tests now follow the requested use-case figures; the Word file is left unchanged. Each report story still has one test.

The compatible `upgrade-db` command adds nullable `category_id` and `category_name` columns to `activity_event`. For old project-creation events, it recovers the available category from surviving projects. Old deleted projects, or earlier category assignments that were never recorded, cannot be reconstructed; unresolved events appear as **Unknown category**. No accounts, projects, shortlists, events, or saved reports are deleted. New activity and its category snapshot are recorded in the same transaction as the successful operation.

The report-content upgrade was applied to the development database on **10 November 2026**. Backup: `backups/before-report-requirements-20261110T050356Z.dump`; its archive manifest was verified. Existing data fingerprints are unchanged across all 11 tables. All 65 sprint tests pass on both SQLite and isolated PostgreSQL test schemas; old-schema upgrades pass twice on both engines; all 208 BCE method contracts and layer checks pass. Restart Flask and generate a new report to see the corrected figures.

## Database upgrade

The upgrade uses the existing `flask --app app upgrade-db` command. It creates company/project tables if the earlier backend upgrade was not applied, and adds:

| Table/change | Purpose |
| --- | --- |
| `category` | Category names, descriptions, unique name index |
| `shortlist` | Unique customer/project saves and saved timestamps |
| `activity_event` | Successful business activity used by reports |
| `report` | Generated period, totals, rows, owner and generation timestamp |
| `interior_design_project.view_count` | Atomic customer view counter |
| Project/category foreign key | Prevent missing category references and deletion of used categories |

For older projects with stored category IDs, the upgrade creates editable `Existing category N` records using the same IDs. It preserves project/account/profile data and advances the PostgreSQL category ID sequence correctly. PostgreSQL receives a foreign key; upgraded SQLite installations also receive equivalent integrity triggers without a table rebuild. Repeating the upgrade is safe.

A PostgreSQL custom-format backup is created under the gitignored `backups/` folder before applying the development upgrade. Existing table row fingerprints are compared afterward. Legacy unused authentication tables are retained. No database reset is performed.

## Validation

The current simplified suite has one test per story: Stories 30–38 in `tests/sprint_4/` and Stories 39–48 in `tests/sprint_5/`. It covers project discovery, saved projects, login/logout, interest counts, categories, and report generation. See [the current test guide](TESTING_GUIDE.md).

```bash
.venv/bin/python -m pytest tests -q
```

The existing CI command `python scripts/run_profile_tests.py` discovers all sprint folders. Earlier implementation verification with Chromium exercised Staff/Customer switching, every staff role, JavaScript-free login, customer discovery/save/remove, category create/update/delete/Cancel, designer project category selection, interest counts, all three report downloads, and desktop/tablet/mobile layouts.

## Applied development upgrade

The PostgreSQL development upgrade was applied successfully on 5 November 2026 (Singapore time). The backup is `backups/before-sprints-4-5-20261105T152649Z.dump`. Its custom archive manifest was checked with `pg_restore --list`.

The original table fingerprints are identical after the upgrade: 4 profiles, 1 account, 1 account-counter row, 3 legacy session rows, and the empty legacy login-attempt table. The six company/project/category/shortlist/activity/report feature tables are ready. No sample accounts or projects were inserted. Thirteen HTML GET routes were checked against the development database after upgrading.

Before the requested test simplification, all 484 tests passed on PostgreSQL using the dedicated `nestora_test` database and unique temporary schemas. The working database was not used for test data.

The previously deleted `boundary/profile/create_user_profile_page.py` was restored from its committed contents because `boundary/routes.py` still imports it; the existing profile flow passes its regression tests.

The final SQLite run also passed all 484 tests. After the final migration adjustment, focused SQLite/PostgreSQL migration checks passed, including preservation of increasing category IDs after deletion and another upgrade. The final Chromium run completed 41 page checks, 13 screenshots and all interactive flows without JavaScript errors, HTTP 500s, or missing assets.

Restart the running Flask process to load the new routes. Start at `/login`, choose Staff or Customer, and select the staff role when applicable. Create a saved category from the manager portal before creating a designer project.
