## Profile tests — Local SQLite

**Test command succeeded.**

53 results · 53 passed · 0 failed · 0 errors · 0 skipped

| Area | Passed | Failed / error | Skipped |
| --- | ---: | ---: | ---: |
| Story 1 | 11 | 0 | 0 |
| Story 2 | 4 | 0 | 0 |
| Story 3 | 7 | 0 | 0 |
| Story 4 | 5 | 0 | 0 |
| Story 5 | 5 | 0 | 0 |
| Security & database | 21 | 0 | 0 |

### Every test result

| ID | Area | Test case | Result | Seconds |
| --- | --- | --- | --- | ---: |
| TC01 | Story 1 | test_TC01_create_form_has_required_fields_and_permission_checkboxes | ✅ PASSED | 0.077 |
| TC02 | Story 1 | test_TC02_create_persists_trimmed_fields_and_selected_permissions | ✅ PASSED | 0.087 |
| TC03 | Story 1 | test_TC03_case_insensitive_duplicate_is_rejected_without_extra_row | ✅ PASSED | 0.093 |
| TC04 | Story 1 | test_TC04_create_rejects_missing_required_field[description] | ✅ PASSED | 0.081 |
| TC04 | Story 1 | test_TC04_create_rejects_missing_required_field[profileName] | ✅ PASSED | 0.081 |
| TC04 | Story 1 | test_TC04_create_rejects_missing_required_field[status] | ✅ PASSED | 0.082 |
| TC05 | Story 1 | test_TC05_create_rejects_unrecognized_choices[unknown-permission] | ✅ PASSED | 0.096 |
| TC05 | Story 1 | test_TC05_create_rejects_unrecognized_choices[unknown-status] | ✅ PASSED | 0.081 |
| TC06 | Story 1 | test_TC06_create_rejects_overlong_text[description-10001] | ✅ PASSED | 0.110 |
| TC06 | Story 1 | test_TC06_create_rejects_overlong_text[profileName-101] | ✅ PASSED | 0.077 |
| TC07 | Story 1 | test_TC07_create_allows_empty_permissions | ✅ PASSED | 0.083 |
| TC08 | Story 2 | test_TC08_directory_displays_profiles_and_statuses | ✅ PASSED | 0.081 |
| TC09 | Story 2 | test_TC09_detail_displays_fields_and_escapes_html | ✅ PASSED | 0.089 |
| TC10 | Story 2 | test_TC10_missing_profile_returns_404 | ✅ PASSED | 0.062 |
| TC11 | Story 2 | test_TC11_profiles_have_predictable_name_order | ✅ PASSED | 0.046 |
| TC12 | Story 3 | test_TC12_update_form_contains_current_values | ✅ PASSED | 0.154 |
| TC13 | Story 3 | test_TC13_update_persists_fields_and_permissions | ✅ PASSED | 0.127 |
| TC14 | Story 3 | test_TC14_duplicate_update_preserves_original_record | ✅ PASSED | 0.117 |
| TC15 | Story 3 | test_TC15_invalid_update_preserves_original_record[description] | ✅ PASSED | 0.128 |
| TC15 | Story 3 | test_TC15_invalid_update_preserves_original_record[profileName] | ✅ PASSED | 0.093 |
| TC15 | Story 3 | test_TC15_invalid_update_preserves_original_record[status] | ✅ PASSED | 0.082 |
| TC16 | Story 3 | test_TC16_update_missing_profile_returns_404 | ✅ PASSED | 0.046 |
| TC17 | Story 4 | test_TC17_suspend_unassigned_profile_persists_status | ✅ PASSED | 0.086 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Active-user_account] | ✅ PASSED | 0.102 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Active-user_accounts] | ✅ PASSED | 0.094 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Suspended-user_account] | ✅ PASSED | 0.093 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Suspended-user_accounts] | ✅ PASSED | 0.095 |
| TC19 | Story 5 | test_TC19_search_matches_profile_name_without_case_sensitivity | ✅ PASSED | 0.070 |
| TC20 | Story 5 | test_TC20_search_matches_description | ✅ PASSED | 0.073 |
| TC21 | Story 5 | test_TC21_no_matching_profiles_shows_empty_message | ✅ PASSED | 0.079 |
| TC22 | Story 5 | test_TC22_blank_search_requests_input[empty] | ✅ PASSED | 0.069 |
| TC22 | Story 5 | test_TC22_blank_search_requests_input[whitespace] | ✅ PASSED | 0.103 |
| TC33 | Security &amp; database | test_TC33_access_denied_without_authenticated_actor_or_preview | ✅ PASSED | 0.059 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[create] | ✅ PASSED | 0.050 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[search] | ✅ PASSED | 0.066 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[suspend] | ✅ PASSED | 0.050 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[update] | ✅ PASSED | 0.046 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[view] | ✅ PASSED | 0.045 |
| TC35 | Security &amp; database | test_TC35_authenticated_actor_can_work_with_preview_disabled | ✅ PASSED | 0.084 |
| TC36 | Security &amp; database | test_TC36_modifying_posts_require_csrf[create] | ✅ PASSED | 0.048 |
| TC36 | Security &amp; database | test_TC36_modifying_posts_require_csrf[suspend] | ✅ PASSED | 0.095 |
| TC36 | Security &amp; database | test_TC36_modifying_posts_require_csrf[update] | ✅ PASSED | 0.066 |
| TC37 | Security &amp; database | test_TC37_modifying_posts_require_permissions_even_with_valid_csrf[create] | ✅ PASSED | 0.108 |
| TC37 | Security &amp; database | test_TC37_modifying_posts_require_permissions_even_with_valid_csrf[suspend] | ✅ PASSED | 0.099 |
| TC37 | Security &amp; database | test_TC37_modifying_posts_require_permissions_even_with_valid_csrf[update] | ✅ PASSED | 0.083 |
| TC38 | Security &amp; database | test_TC38_controller_also_rejects_unauthorized_calls | ✅ PASSED | 0.021 |
| TC39 | Security &amp; database | test_TC39_legacy_upgrade_preserves_profile_and_adds_status[user_profile] | ✅ PASSED | 0.036 |
| TC39 | Security &amp; database | test_TC39_legacy_upgrade_preserves_profile_and_adds_status[user_profiles] | ✅ PASSED | 0.036 |
| TC40 | Security &amp; database | test_TC40_upgrade_stops_for_duplicate_names_without_deleting_rows | ✅ PASSED | 0.026 |
| TC41 | Security &amp; database | test_TC41_upgrade_rejects_unknown_schema_without_deleting_table | ✅ PASSED | 0.023 |
| TC42 | Security &amp; database | test_TC42_ambiguous_existing_account_schema_blocks_suspension | ✅ PASSED | 0.105 |
| TC43 | Security &amp; database | test_TC43_permission_storage_type_matches_database_and_round_trips | ✅ PASSED | 0.025 |
| TC44 | Security &amp; database | test_TC44_unsupported_directory_operation_is_rejected | ✅ PASSED | 0.049 |

Download the job’s report artifact and open `test-results.html` for filters and assertion details, or `coverage/index.html` for executed code lines.

Parameterized tests have one row per input. Skipped tests are not passes. Coverage is a separate measurement from test success.
