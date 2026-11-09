## Sprint 1–5 tests — Local SQLite

**Test command succeeded.**

65 results · 65 passed · 0 failed · 0 errors · 0 skipped

| Sprint | Stories | Passed | Failed / error | Skipped |
| --- | --- | ---: | ---: | ---: |
| Sprint 1 | 1–5 | 22 | 0 | 0 |
| Sprint 2 | 6–17 | 12 | 0 | 0 |
| Sprint 3 | 18–29 | 12 | 0 | 0 |
| Sprint 4 | 30–38 | 9 | 0 | 0 |
| Sprint 5 | 39–48 | 10 | 0 | 0 |

### Every test result

| ID | Sprint | Story | Test case | Result | Seconds |
| --- | --- | --- | --- | --- | ---: |
| TC01 | Sprint 1 | 1 | test_TC01_create_form_renders_and_incomplete_submission_is_not_saved | ✅ PASSED | 0.454 |
| TC02 | Sprint 1 | 1 | test_TC02_valid_submission_saves_fields_and_permissions | ✅ PASSED | 0.356 |
| TC03 | Sprint 1 | 1 | test_TC03_duplicate_names_are_rejected_regardless_of_capitalization | ✅ PASSED | 0.347 |
| TC04 | Sprint 1 | 1 | test_TC04_each_missing_required_field_is_rejected | ✅ PASSED | 0.356 |
| TC05 | Sprint 1 | 1 | test_TC05_unknown_status_is_rejected | ✅ PASSED | 0.335 |
| TC06 | Sprint 1 | 1 | test_TC06_overlong_names_and_descriptions_are_rejected | ✅ PASSED | 0.325 |
| TC07 | Sprint 1 | 1 | test_TC07_profile_can_be_created_without_permissions | ✅ PASSED | 0.311 |
| TC08 | Sprint 1 | 2 | test_TC08_list_displays_active_and_suspended_profiles_with_statuses | ✅ PASSED | 0.388 |
| TC09 | Sprint 1 | 2 | test_TC09_profile_details_are_correct | ✅ PASSED | 0.352 |
| TC10 | Sprint 1 | 2 | test_TC10_viewing_nonexistent_profile_returns_error | ✅ PASSED | 0.296 |
| TC11 | Sprint 1 | 2 | test_TC11_profiles_are_listed_in_alphabetical_order | ✅ PASSED | 0.370 |
| TC12 | Sprint 1 | 3 | test_TC12_update_form_displays_existing_fields_and_selected_permissions | ✅ PASSED | 0.355 |
| TC13 | Sprint 1 | 3 | test_TC13_changes_are_saved_accurately | ✅ PASSED | 0.359 |
| TC14 | Sprint 1 | 3 | test_TC14_duplicate_name_is_rejected_and_original_record_is_unchanged | ✅ PASSED | 0.351 |
| TC15 | Sprint 1 | 3 | test_TC15_missing_required_update_fields_are_rejected | ✅ PASSED | 0.337 |
| TC16 | Sprint 1 | 3 | test_TC16_updating_nonexistent_profile_returns_error | ✅ PASSED | 0.325 |
| TC17 | Sprint 1 | 4 | test_TC17_unassigned_profile_can_be_suspended_and_status_is_saved | ✅ PASSED | 0.383 |
| TC18 | Sprint 1 | 4 | test_TC18_assigned_profile_cannot_be_suspended | ✅ PASSED | 0.421 |
| TC19 | Sprint 1 | 5 | test_TC19_search_by_name_is_case_insensitive | ✅ PASSED | 0.384 |
| TC20 | Sprint 1 | 5 | test_TC20_search_returns_existing_profile | ✅ PASSED | 0.338 |
| TC21 | Sprint 1 | 5 | test_TC21_unmatched_search_displays_no_profiles_found | ✅ PASSED | 0.347 |
| TC22 | Sprint 1 | 5 | test_TC22_empty_or_whitespace_search_displays_validation_message | ✅ PASSED | 0.358 |
| US06 | Sprint 2 | 6 | test_create_user_account_saves_details_and_default_password | ✅ PASSED | 0.591 |
| US07 | Sprint 2 | 7 | test_view_user_account_displays_saved_details | ✅ PASSED | 0.429 |
| US08 | Sprint 2 | 8 | test_update_user_account_loads_and_saves_details | ✅ PASSED | 0.439 |
| US09 | Sprint 2 | 9 | test_suspend_user_account_saves_suspended_status | ✅ PASSED | 0.390 |
| US10 | Sprint 2 | 10 | test_search_user_account_returns_matching_account | ✅ PASSED | 0.401 |
| US11 | Sprint 2 | 11 | test_user_admin_login_opens_dashboard | ✅ PASSED | 0.382 |
| US12 | Sprint 2 | 12 | test_user_admin_logout_clears_login_and_returns_to_login_page | ✅ PASSED | 0.297 |
| US13 | Sprint 2 | 13 | test_create_company_profile_saves_company_details | ✅ PASSED | 0.297 |
| US14 | Sprint 2 | 14 | test_view_company_profile_displays_saved_details | ✅ PASSED | 0.312 |
| US15 | Sprint 2 | 15 | test_delete_company_profile_removes_saved_profile | ✅ PASSED | 0.392 |
| US16 | Sprint 2 | 16 | test_update_company_profile_loads_and_saves_company_details | ✅ PASSED | 0.346 |
| US17 | Sprint 2 | 17 | test_search_company_profile_returns_matching_details | ✅ PASSED | 0.314 |
| US18 | Sprint 3 | 18 | test_interior_designer_login_opens_dashboard | ✅ PASSED | 0.365 |
| US19 | Sprint 3 | 19 | test_interior_designer_logout_clears_login_and_returns_to_login_page | ✅ PASSED | 0.286 |
| US20 | Sprint 3 | 20 | test_create_new_project_saves_project_details | ✅ PASSED | 0.327 |
| US21 | Sprint 3 | 21 | test_update_new_project_loads_and_saves_project_details | ✅ PASSED | 0.334 |
| US22 | Sprint 3 | 22 | test_view_new_project_displays_saved_details | ✅ PASSED | 0.306 |
| US23 | Sprint 3 | 23 | test_search_new_projects_returns_matching_project | ✅ PASSED | 0.314 |
| US24 | Sprint 3 | 24 | test_delete_new_project_removes_saved_project | ✅ PASSED | 0.420 |
| US25 | Sprint 3 | 25 | test_create_past_project_saves_project_details | ✅ PASSED | 0.312 |
| US26 | Sprint 3 | 26 | test_view_past_project_displays_saved_details | ✅ PASSED | 0.337 |
| US27 | Sprint 3 | 27 | test_update_past_project_loads_and_saves_project_details | ✅ PASSED | 0.331 |
| US28 | Sprint 3 | 28 | test_search_past_projects_returns_matching_project | ✅ PASSED | 0.316 |
| US29 | Sprint 3 | 29 | test_delete_past_project_removes_saved_project | ✅ PASSED | 0.457 |
| US30 | Sprint 4 | 30 | test_customer_search_returns_matching_project | ✅ PASSED | 0.406 |
| US31 | Sprint 4 | 31 | test_customer_view_displays_project_details | ✅ PASSED | 0.419 |
| US32 | Sprint 4 | 32 | test_customer_saves_project_to_shortlist | ✅ PASSED | 0.483 |
| US33 | Sprint 4 | 33 | test_customer_searches_saved_projects | ✅ PASSED | 0.415 |
| US34 | Sprint 4 | 34 | test_customer_views_saved_project_details | ✅ PASSED | 0.404 |
| US35 | Sprint 4 | 35 | test_customer_login_opens_dashboard | ✅ PASSED | 0.359 |
| US36 | Sprint 4 | 36 | test_customer_logout_clears_login_and_returns_to_login_page | ✅ PASSED | 0.302 |
| US37 | Sprint 4 | 37 | test_designer_views_saved_project_view_count | ✅ PASSED | 0.327 |
| US38 | Sprint 4 | 38 | test_designer_views_project_shortlist_count | ✅ PASSED | 0.398 |
| US39 | Sprint 5 | 39 | test_platform_manager_login_opens_dashboard | ✅ PASSED | 0.380 |
| US40 | Sprint 5 | 40 | test_platform_manager_logout_clears_login_and_returns_to_login_page | ✅ PASSED | 0.294 |
| US41 | Sprint 5 | 41 | test_create_category_saves_category_details | ✅ PASSED | 0.299 |
| US42 | Sprint 5 | 42 | test_view_category_displays_saved_details | ✅ PASSED | 0.311 |
| US43 | Sprint 5 | 43 | test_update_category_loads_and_saves_category_details | ✅ PASSED | 0.368 |
| US44 | Sprint 5 | 44 | test_delete_category_removes_saved_category | ✅ PASSED | 0.303 |
| US45 | Sprint 5 | 45 | test_search_categories_returns_matching_category | ✅ PASSED | 0.321 |
| US46 | Sprint 5 | 46 | test_generate_daily_report_displays_and_saves_period_totals | ✅ PASSED | 0.325 |
| US47 | Sprint 5 | 47 | test_generate_weekly_report_displays_and_saves_period_totals | ✅ PASSED | 0.341 |
| US48 | Sprint 5 | 48 | test_generate_monthly_report_displays_and_saves_period_totals | ✅ PASSED | 0.320 |

Sprint 1 uses the Word document’s TC01–TC22 checks. Sprints 2–5 have one test per story (US06–US48).

Open `test-results.html` for filters and assertion details, or `coverage/index.html` for executed code lines. Skipped tests are not passes. Coverage is separate from test success.
