# BCE audit — User Stories 1–48

Source: `Nothinghere/CSIT314 Group Project Report (4).docx`. All 48 embedded BCE diagrams were inspected in story order. The retained diagram transcription is `docs/bce_contracts.json`; the earlier contract tests checked class names, every diagram method, parameter names/order/types, return types, and void event/display signatures.

## Layer responsibilities

- Boundaries receive HTTP input, clean and validate required fields/types/lengths, and prepare HTML, messages, redirects, or JSON.
- Controllers relay calls and entity results. They do not read HTTP input, validate text, or execute SQL.
- Entities perform queries, duplicate/reference checks, business state changes, counters, and transactions.
- Database/migration infrastructure supplies the connection and compatibility adapters. HTTP `get`/`post`, prefill getters, serialization helpers, and constructor account context support the diagram operations.
- UML `void` is represented by `-> None`. Event/display methods prepare `self.rendered_page`; the HTTP adapter returns it.

## Story-by-story result

| Story | Boundary and diagram methods | Controller operation | Entity operation | Result |
| --- | --- | --- | --- | --- |
| 1 | [CreateUserProfilePage](../boundary/profile/create_user_profile_page.py)<br>`onCreate(profileName, description, status, permissions)`; `displaySuccess()`; `displayError()` | `CreateUserProfileController.createUserProfile` | `UserProfile`<br>`createUserProfile`, `userProfileExists` | Changed status from bool to str through B/C/E; made userProfileExists(profileName) exact. |
| 2 | [ViewUserProfilePage](../boundary/profile/view_user_profile_page.py)<br>`onView(profileId)`; `displayProfile(profile)` | `ViewUserProfileController.getUserProfile` | `UserProfile`<br>`getUserProfile` | Resolved UserProfile display type imports and consistent void annotations. |
| 3 | [UpdateUserProfilePage](../boundary/profile/update_user_profile_page.py)<br>`onUpdate(profileId, profileName, description, permissions)`; `displaySuccess()`; `displayError()` | `UpdateUserProfileController.updateUserProfile` | `UserProfile`<br>`updateUserProfile` | Verified against the updated diagram; no story interface change needed. |
| 4 | [SuspendUserProfilePage](../boundary/profile/suspend_user_profile_page.py)<br>`onSuspend(profileId)`; `displaySuccess()` | `SuspendUserProfileController.suspendUserProfile` | `UserProfile`<br>`suspendUserProfile` | Verified against the updated diagram; no story interface change needed. |
| 5 | [SearchUserProfilePage](../boundary/profile/search_user_profile_page.py)<br>`onSearch(keyword)`; `displayResults(profiles)` | `SearchUserProfileController.searchUserProfiles` | `UserProfile`<br>`searchUserProfiles` | Resolved UserProfile results type imports and consistent void annotations. |
| 6 | [CreateUserAccountPage](../boundary/accounts/create_user_account_page.py)<br>`onCreate(username, fullName, email, phoneNumber, profileId)`; `displaySuccess()`; `displayError()` | `CreateUserAccountController.createUserAccount` | `UserAccount`<br>`createUserAccount`, `userAccountExists`, `generateAccountId` | Renamed clickCreate to onCreate. Approved password-free creation retained. |
| 7 | [ViewUserAccountPage](../boundary/accounts/view_user_account_page.py)<br>`onView(accountId)`; `displayAccount(account)` | `ViewUserAccountController.getUserAccount` | `UserAccount`<br>`getUserAccount` | Resolved UserAccount display type imports and consistent void annotations. |
| 8 | [UpdateUserAccountPage](../boundary/accounts/update_user_account_page.py)<br>`onUpdate(accountId, fullName, email, profileId)`; `displaySuccess()`; `displayError()` | `UpdateUserAccountController.updateUserAccount` | `UserAccount`<br>`updateUserAccount` | Verified against the updated diagram; no story interface change needed. |
| 9 | [SuspendUserAccountPage](../boundary/accounts/suspend_user_account_page.py)<br>`onSuspend(accountId)`; `displaySuccess()` | `SuspendUserAccountController.suspendUserAccount` | `UserAccount`<br>`suspendUserAccount` | Verified against the updated diagram; no story interface change needed. |
| 10 | [SearchUserAccountPage](../boundary/accounts/search_user_account_page.py)<br>`onSearch(keyword)`; `displayResults(accounts)` | `SearchUserAccountController.searchUserAccounts` | `UserAccount`<br>`searchUserAccounts` | Resolved UserAccount results type imports and consistent void annotations. |
| 11 | [UserAdminLoginPage](../boundary/auth/user_admin_login_page.py)<br>`onLogin(username, password)`; `displayDashboard()`; `displayError()` | `UserAdminLoginController.login` | `UserAccount`<br>`login` | Renamed LoginPage/LoginController/clickLogin to the diagram UserAdmin names and onLogin. |
| 12 | [LogoutPage](../boundary/auth/logout_page.py)<br>`logout()`; `displayLoginPage()` | — (diagram has no controller methods) | — (diagram has no entity methods) | Verified against the updated diagram; no story interface change needed. |
| 13 | [CreateCompanyProfilePage](../boundary/company/create_company_profile_page.py)<br>`onCreate(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)`; `displaySuccess()`; `displayError()` | `CreateCompanyProfileController.createCompanyProfile` | `CompanyProfile`<br>`createCompanyProfile` | Verified against the updated diagram; no story interface change needed. |
| 14 | [ViewCompanyProfilePage](../boundary/company/view_company_profile_page.py)<br>`onView()`; `displayCompanyProfile(profile)` | `ViewCompanyProfileController.getCompanyProfile` | `CompanyProfile`<br>`getCompanyProfile` | Verified against the updated diagram; no story interface change needed. |
| 15 | [DeleteCompanyProfilePage](../boundary/company/delete_company_profile_page.py)<br>`onDelete()`; `displaySuccess()` | `DeleteCompanyProfileController.deleteCompanyProfile` | `CompanyProfile`<br>`deleteCompanyProfile` | Verified against the updated diagram; no story interface change needed. |
| 16 | [UpdateCompanyProfilePage](../boundary/company/update_company_profile_page.py)<br>`onUpdate(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)`; `displaySuccess()`; `displayError()` | `UpdateCompanyProfileController.updateCompanyProfile` | `CompanyProfile`<br>`updateCompanyProfile` | Verified against the updated diagram; no story interface change needed. |
| 17 | [SearchCompanyProfilePage](../boundary/company/search_company_profile_page.py)<br>`onSearch(keyword)`; `displayResults(results)` | `SearchCompanyProfileController.searchCompanyProfile` | `CompanyProfile`<br>`searchCompanyProfile` | Verified against the updated diagram; no story interface change needed. |
| 18 | [InteriorDesignerLoginPage](../boundary/designer/interior_designer_login_page.py)<br>`onLogin(username, password)`; `displayDashboard()`; `displayError()` | `InteriorDesignerLoginController.login` | `UserAccount`<br>`login` | Verified against the updated diagram; no story interface change needed. |
| 19 | [InteriorDesignerLogoutPage](../boundary/designer/interior_designer_logout_page.py)<br>`logout()`; `displayLoginPage()` | — (diagram has no controller methods) | — (diagram has no entity methods) | Verified against the updated diagram; no story interface change needed. |
| 20 | [CreateNewProjectPage](../boundary/projects/create_new_project_page.py)<br>`onCreate(projectName, categoryId, propertyType, area, renovationCost, description)`; `displaySuccess()`; `displayError()` | `CreateNewProjectController.createNewProject` | `InteriorDesignProject`<br>`createNewProject` | Verified against the updated diagram; no story interface change needed. |
| 21 | [UpdateNewProjectPage](../boundary/projects/update_new_project_page.py)<br>`onUpdate(projectId, projectName, categoryId, propertyType, area, renovationCost, description)`; `displaySuccess()`; `displayError()` | `UpdateNewProjectController.updateNewProject` | `InteriorDesignProject`<br>`updateNewProject` | Verified against the updated diagram; no story interface change needed. |
| 22 | [ViewNewProjectPage](../boundary/projects/view_new_project_page.py)<br>`onView(projectId)`; `displayProject(project)` | `ViewNewProjectController.getNewProject` | `InteriorDesignProject`<br>`getNewProject` | Verified against the updated diagram; no story interface change needed. |
| 23 | [SearchNewProjectPage](../boundary/projects/search_new_project_page.py)<br>`onSearch(projectName)`; `displayResults(projects)` | `SearchNewProjectController.searchNewProjects` | `InteriorDesignProject`<br>`searchNewProjects` | Verified against the updated diagram; no story interface change needed. |
| 24 | [DeleteNewProjectPage](../boundary/projects/delete_new_project_page.py)<br>`onDelete(projectId)`; `displaySuccess()` | `DeleteNewProjectController.deleteNewProject` | `InteriorDesignProject`<br>`deleteNewProject` | Verified against the updated diagram; no story interface change needed. |
| 25 | [CreatePastProjectPage](../boundary/projects/create_past_project_page.py)<br>`onCreate(projectName, categoryId, propertyType, area, renovationCost, description)`; `displaySuccess()`; `displayError()` | `CreatePastProjectController.createPastProject` | `InteriorDesignProject`<br>`createPastProject` | Verified against the updated diagram; no story interface change needed. |
| 26 | [ViewPastProjectPage](../boundary/projects/view_past_project_page.py)<br>`onView(projectId)`; `displayProject(project)` | `ViewPastProjectController.getPastProject` | `InteriorDesignProject`<br>`getPastProject` | Verified against the updated diagram; no story interface change needed. |
| 27 | [UpdatePastProjectPage](../boundary/projects/update_past_project_page.py)<br>`onUpdate(projectId, projectName, categoryId, propertyType, area, renovationCost, description)`; `displaySuccess()`; `displayError()` | `UpdatePastProjectController.updatePastProject` | `InteriorDesignProject`<br>`updatePastProject` | Verified against the updated diagram; no story interface change needed. |
| 28 | [SearchPastProjectPage](../boundary/projects/search_past_project_page.py)<br>`onSearch(projectName)`; `displayResults(projects)` | `SearchPastProjectController.searchPastProjects` | `InteriorDesignProject`<br>`searchPastProjects` | Verified against the updated diagram; no story interface change needed. |
| 29 | [DeletePastProjectPage](../boundary/projects/delete_past_project_page.py)<br>`onDelete(projectId)`; `displaySuccess()` | `DeletePastProjectController.deletePastProject` | `InteriorDesignProject`<br>`deletePastProject` | Verified against the updated diagram; no story interface change needed. |
| 30 | [SearchIDPPage](../boundary/customer/search_idp_page.py)<br>`onSearch(keyword)`; `displayResults(idps)` | `SearchIDPController.search_all_IDPs` | `InteriorDesignProject`<br>`search_all_IDPs` | Verified against the updated diagram; no story interface change needed. |
| 31 | [ViewIDPPage](../boundary/customer/view_idp_page.py)<br>`onView(projectId)`; `displayIDP(idp)` | `ViewIDPController.getIDP` | `InteriorDesignProject`<br>`getIDP`, `incrementViewCount` | Verified against the updated diagram; no story interface change needed. |
| 32 | [SaveShortlistIDPPage](../boundary/customer/save_shortlist_idp_page.py)<br>`onSave(projectId)`; `displaySuccess()`; `displayError()` | `SaveShortlistIDPController.saveShortlist` | `Shortlist`<br>`saveShortlist` | Verified against the updated diagram; no story interface change needed. |
| 33 | [SearchShortlistIDPPage](../boundary/customer/search_shortlist_idp_page.py)<br>`onSearch(keyword)`; `displayResults(idps)` | `SearchShortlistIDPController.search_shortlist_IDP` | `InteriorDesignProject`<br>`search_shortlist_IDP` | Verified against the updated diagram; no story interface change needed. |
| 34 | [ViewShortlistIDPPage](../boundary/customer/view_shortlist_idp_page.py)<br>`onView(projectId)`; `displayIDP(idp)` | `ViewShortlistIDPController.getIDP` | `InteriorDesignProject`<br>`getIDP`, `incrementViewCount` | Verified against the updated diagram; no story interface change needed. |
| 35 | [CustomerLoginPage](../boundary/customer/customer_login_page.py)<br>`onLogin(username, password)`; `displayDashboard()`; `displayError()` | `CustomerLoginController.login` | `UserAccount`<br>`login` | Verified against the updated diagram; no story interface change needed. |
| 36 | [LogoutPage](../boundary/customer/logout_page.py)<br>`logout()`; `displayLoginPage()` | — (diagram has no controller methods) | — (diagram has no entity methods) | Verified against the updated diagram; no story interface change needed. |
| 37 | [ViewCountPage](../boundary/designer/view_count_page.py)<br>`onView(projectId)`; `displayViewCount(viewCount)` | `ViewCountController.getViewCount` | `InteriorDesignProject`<br>`getViewCount` | Verified against the updated diagram; no story interface change needed. |
| 38 | [ViewShortlistCountPage](../boundary/designer/view_shortlist_count_page.py)<br>`onView(projectId)`; `displayShortlistCount(shortlistCount)` | `ViewShortlistCountController.getShortlistCount` | `Shortlist`<br>`getShortlistCount` | Verified against the updated diagram; no story interface change needed. |
| 39 | [PlatformManagerLoginPage](../boundary/platform_manager/platform_manager_login_page.py)<br>`onLogin(username, password)`; `displayDashboard()`; `displayError()` | `PlatformManagerLoginController.login` | `UserAccount`<br>`login` | Verified against the updated diagram; no story interface change needed. |
| 40 | [PlatformManagerLogoutPage](../boundary/platform_manager/platform_manager_logout_page.py)<br>`logout()`; `displayLoginPage()` | — (diagram has no controller methods) | — (diagram has no entity methods) | Verified against the updated diagram; no story interface change needed. |
| 41 | [CreateCategoryPage](../boundary/categories/create_category_page.py)<br>`onCreate(categoryName, description)`; `displaySuccess()`; `displayError()` | `CreateCategoryController.createCategory` | `Category`<br>`createCategory`, `categoryExists` | Verified against the updated diagram; no story interface change needed. |
| 42 | [ViewCategoryPage](../boundary/categories/view_category_page.py)<br>`onView(categoryId)`; `displayCategory(category)` | `ViewCategoryController.getCategory` | `Category`<br>`getCategory` | Verified against the updated diagram; no story interface change needed. |
| 43 | [UpdateCategoryPage](../boundary/categories/update_category_page.py)<br>`onUpdate(categoryId, categoryName, description)`; `displaySuccess()`; `displayError()` | `UpdateCategoryController.updateCategory` | `Category`<br>`updateCategory` | Verified against the updated diagram; no story interface change needed. |
| 44 | [DeleteCategoryPage](../boundary/categories/delete_category_page.py)<br>`onDelete(categoryId)`; `displaySuccess()` | `DeleteCategoryController.deleteCategory` | `Category`<br>`deleteCategory` | Verified against the updated diagram; no story interface change needed. |
| 45 | [SearchCategoryPage](../boundary/categories/search_category_page.py)<br>`onSearch(keyword)`; `displayResults(categories)` | `SearchCategoryController.searchCategories` | `Category`<br>`searchCategories` | Verified against the updated diagram; no story interface change needed. |
| 46 | [DailyReportPage](../boundary/reports/daily_report_page.py)<br>`onGenerateDailyReport(startDate)`; `displayReport(report)` | `DailyReportController.generateDailyReport` | `Report`<br>`generateReport` | Replaced inferred report interface with DailyReportPage and DailyReportController; startDate only. |
| 47 | [WeeklyReportPage](../boundary/reports/weekly_report_page.py)<br>`onGenerateWeeklyReport(startDate)`; `displayReport(report)` | `WeeklyReportController.generateWeeklyReport` | `Report`<br>`generateReport` | Replaced inferred report interface with WeeklyReportPage and WeeklyReportController; startDate only. |
| 48 | [MonthlyReportPage](../boundary/reports/monthly_report_page.py)<br>`onGenerateMonthlyReport(startDate, endDate)`; `displayReport(report)` | `MonthlyReportController.generateMonthlyReport` | `Report`<br>`generateReport` | Replaced inferred report interface with MonthlyReportPage and MonthlyReportController; both dates. |

## Approved Story 6 exception

The Word diagram includes a password argument for account creation. The user explicitly chose password-free admin account creation earlier in this project. The boundary/controller creation interfaces therefore omit that password input. The entity keeps the existing keyword-only password argument for trusted terminal setup, with no usable password generated by the web form. This is the only intentional diagram exception.

## Report interfaces and dates

- `DailyReportPage.onGenerateDailyReport(startDate: date) -> None` calls `DailyReportController.generateDailyReport(startDate: date) -> Report`.
- `WeeklyReportPage.onGenerateWeeklyReport(startDate: date) -> None` calls `WeeklyReportController.generateWeeklyReport(startDate: date) -> Report`.
- `MonthlyReportPage.onGenerateMonthlyReport(startDate: date, endDate: date) -> None` calls `MonthlyReportController.generateMonthlyReport(startDate: date, endDate: date) -> Report`.
- Every report page has `displayReport(report: Report) -> None`.
- Controllers create an entity with optional account context and call `Report.generateReport(reportType: str, startDate: date, endDate: date) -> Report`.
- Weekly end-date derivation is an entity helper. Date-input checks remain in the boundary. Daily/weekly end dates are shown read-only; monthly retains two editable date fields. Legacy HTTP clients may still submit a matching end date.
- Existing report snapshots, CSV exports, Singapore date boundaries, and URL endpoints are preserved.

## Database alignment

Profile status already uses a string column; no account/profile data conversion is needed. The report schema gains checks for supported report types and non-reversed date ranges. The normal additive upgrade creates missing tables and preserves existing IDs, passwords, snapshots, and relationships. SQLite upgrade triggers provide the equivalent integrity checks on older SQLite tables.

## Audit evidence

- 48/48 story diagrams are represented in the independent contract manifest.
- All listed void methods were inspected for non-void returns; none return a value.
- Static layer checks reject database imports in boundaries/controllers and HTTP/input-layer imports in entities.
- Full regression and database verification results are recorded below.

## Completed verification (before sprint test simplification)

- **547 tests passed on SQLite.**
- **547 tests passed on PostgreSQL**, using the dedicated test database and isolated schemas.
- The full 48-story contract suite passes, including every event/display signature and the shared report entity method.
- Chromium exercised all login roles, Staff/Customer switching, customer shortlists, category management, designer interest counts, project category selection, all report generations/downloads, keyboard controls, and JavaScript-free login. Desktop, tablet, and mobile checks passed without JavaScript errors, HTTP 500s, or missing assets.
- The PostgreSQL development upgrade was applied. All nine active entity tables match their model column names, type families, and nullability. The report type/date-range checks are present.
- Every existing application-table row fingerprint matches the pre-upgrade backup; no data reset or password change was performed. Thirteen HTML routes passed against the development database after upgrading.

Backup: `backups/before-bce-audit-20261107T163947Z.dump` (gitignored PostgreSQL custom-format archive, verified using `pg_restore --list`).

Restart the running Flask process to load the renamed Python modules. The web URLs remain the same, including `/login`, `/staff/login`, and `/manager/reports/daily`, `/weekly`, and `/monthly`.

## Current test organisation

The earlier 547-test audit results above are historical evidence. The requested simplified suite now lives in `tests/sprint_1/` through `tests/sprint_5/`: 22 documented Sprint 1 checks and one test per later story (65 total). The broad contract and regression suites were removed; the manifest remains here as a diagram reference. See [the current test guide](TESTING_GUIDE.md).
