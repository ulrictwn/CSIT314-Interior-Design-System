## User Admin tests — Local SQLite

**Test command succeeded.**

111 results · 111 passed · 0 failed · 0 errors · 0 skipped

| Area | Passed | Failed / error | Skipped |
| --- | ---: | ---: | ---: |
| Story 1 | 14 | 0 | 0 |
| Story 2 | 4 | 0 | 0 |
| Story 3 | 7 | 0 | 0 |
| Story 4 | 5 | 0 | 0 |
| Story 5 | 5 | 0 | 0 |
| Story 6 | 24 | 0 | 0 |
| Story 7 | 2 | 0 | 0 |
| Story 8 | 4 | 0 | 0 |
| Story 9 | 1 | 0 | 0 |
| Story 10 | 6 | 0 | 0 |
| Story 11 | 6 | 0 | 0 |
| Story 12 | 1 | 0 | 0 |
| Security & database | 32 | 0 | 0 |

### Every test result

| ID | Area | Test case | Result | Seconds |
| --- | --- | --- | --- | ---: |
| TC01.1 | Story 1 | test_TC01_create_form_checks[TC01.1] | ✅ PASSED | 0.123 |
| TC01.2 | Story 1 | test_TC01_create_form_checks[TC01.2] | ✅ PASSED | 0.125 |
| TC01.3 | Story 1 | test_TC01_create_form_checks[TC01.3] | ✅ PASSED | 0.132 |
| TC01.4 | Story 1 | test_TC01_create_form_checks[TC01.4] | ✅ PASSED | 0.137 |
| TC02 | Story 1 | test_TC02_create_persists_trimmed_fields_and_selected_permissions | ✅ PASSED | 0.130 |
| TC03 | Story 1 | test_TC03_case_insensitive_duplicate_is_rejected_without_extra_row | ✅ PASSED | 0.176 |
| TC04 | Story 1 | test_TC04_create_rejects_missing_required_field[description] | ✅ PASSED | 0.122 |
| TC04 | Story 1 | test_TC04_create_rejects_missing_required_field[profileName] | ✅ PASSED | 0.122 |
| TC04 | Story 1 | test_TC04_create_rejects_missing_required_field[status] | ✅ PASSED | 0.132 |
| TC05 | Story 1 | test_TC05_create_rejects_unrecognized_choices[unknown-permission] | ✅ PASSED | 0.119 |
| TC05 | Story 1 | test_TC05_create_rejects_unrecognized_choices[unknown-status] | ✅ PASSED | 0.123 |
| TC06 | Story 1 | test_TC06_create_rejects_overlong_text[description-10001] | ✅ PASSED | 0.137 |
| TC06 | Story 1 | test_TC06_create_rejects_overlong_text[profileName-101] | ✅ PASSED | 0.130 |
| TC07 | Story 1 | test_TC07_create_allows_empty_permissions | ✅ PASSED | 0.168 |
| TC08 | Story 2 | test_TC08_directory_displays_profiles_and_statuses | ✅ PASSED | 0.124 |
| TC09 | Story 2 | test_TC09_detail_displays_fields_and_escapes_html | ✅ PASSED | 0.118 |
| TC10 | Story 2 | test_TC10_missing_profile_returns_404 | ✅ PASSED | 0.075 |
| TC11 | Story 2 | test_TC11_profiles_have_predictable_name_order | ✅ PASSED | 0.053 |
| TC12 | Story 3 | test_TC12_update_form_contains_current_values | ✅ PASSED | 0.131 |
| TC13 | Story 3 | test_TC13_update_persists_fields_and_permissions | ✅ PASSED | 0.213 |
| TC14 | Story 3 | test_TC14_duplicate_update_preserves_original_record | ✅ PASSED | 0.195 |
| TC15 | Story 3 | test_TC15_invalid_update_preserves_original_record[description] | ✅ PASSED | 0.203 |
| TC15 | Story 3 | test_TC15_invalid_update_preserves_original_record[profileName] | ✅ PASSED | 0.227 |
| TC15 | Story 3 | test_TC15_invalid_update_preserves_original_record[status] | ✅ PASSED | 0.137 |
| TC16 | Story 3 | test_TC16_update_missing_profile_returns_404 | ✅ PASSED | 0.069 |
| TC17 | Story 4 | test_TC17_suspend_unassigned_profile_persists_status | ✅ PASSED | 0.146 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Active-user_account] | ✅ PASSED | 0.222 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Active-user_accounts] | ✅ PASSED | 0.186 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Suspended-user_account] | ✅ PASSED | 0.144 |
| TC18 | Story 4 | test_TC18_assigned_profile_cannot_be_suspended[Suspended-user_accounts] | ✅ PASSED | 0.200 |
| TC19 | Story 5 | test_TC19_search_matches_profile_name_without_case_sensitivity | ✅ PASSED | 0.189 |
| TC20 | Story 5 | test_TC20_search_matches_description | ✅ PASSED | 0.267 |
| TC21 | Story 5 | test_TC21_no_matching_profiles_shows_empty_message | ✅ PASSED | 0.164 |
| TC22 | Story 5 | test_TC22_blank_search_requests_input[empty] | ✅ PASSED | 0.114 |
| TC22 | Story 5 | test_TC22_blank_search_requests_input[whitespace] | ✅ PASSED | 0.112 |
| TC23 | Story 6 | test_TC23_account_id_matches_assigned_role[Customer-202] | ✅ PASSED | 0.437 |
| TC23 | Story 6 | test_TC23_account_id_matches_assigned_role[Interior Designer-302] | ✅ PASSED | 0.439 |
| TC23 | Story 6 | test_TC23_account_id_matches_assigned_role[Platform Management-402] | ✅ PASSED | 0.463 |
| TC23 | Story 6 | test_TC23_account_id_matches_assigned_role[User Admin-102] | ✅ PASSED | 0.453 |
| TC24 | Story 6 | test_TC24_ids_increment_and_no_password_is_required | ✅ PASSED | 0.553 |
| TC25 | Story 6 | test_TC25_duplicate_username_is_rejected | ✅ PASSED | 0.443 |
| TC26 | Story 6 | test_TC26_invalid_create_does_not_save[email] | ✅ PASSED | 0.453 |
| TC26 | Story 6 | test_TC26_invalid_create_does_not_save[full_name] | ✅ PASSED | 0.505 |
| TC26 | Story 6 | test_TC26_invalid_create_does_not_save[phone_number] | ✅ PASSED | 0.452 |
| TC26 | Story 6 | test_TC26_invalid_create_does_not_save[profile_id] | ✅ PASSED | 0.440 |
| TC26 | Story 6 | test_TC26_invalid_create_does_not_save[username] | ✅ PASSED | 0.413 |
| TC27 | Story 6 | test_TC27_inactive_profile_cannot_be_assigned | ✅ PASSED | 0.470 |
| TC28 | Story 7 | test_TC28_view_account_displays_details_without_password | ✅ PASSED | 0.428 |
| TC29 | Story 7 | test_TC29_missing_account_returns_404 | ✅ PASSED | 0.474 |
| TC30 | Story 8 | test_TC30_update_preserves_id_username_password_and_status | ✅ PASSED | 0.473 |
| TC31 | Story 8 | test_TC31_invalid_update_preserves_values | ✅ PASSED | 0.433 |
| TC32 | Story 8 | test_TC32_cancel_is_navigation_and_does_not_update | ✅ PASSED | 0.500 |
| TC33 | Security &amp; database | test_TC33_access_denied_without_authenticated_actor_or_preview | ✅ PASSED | 0.107 |
| TC33 | Story 8 | test_TC33_last_admin_cannot_be_reassigned | ✅ PASSED | 0.442 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[create] | ✅ PASSED | 0.085 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[search] | ✅ PASSED | 0.084 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[suspend] | ✅ PASSED | 0.073 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[update] | ✅ PASSED | 0.094 |
| TC34 | Security &amp; database | test_TC34_authenticated_actor_needs_permission_for_each_page[view] | ✅ PASSED | 0.081 |
| TC34 | Story 9 | test_TC34_suspend_retains_data_and_rejects_repeated_suspension | ✅ PASSED | 0.509 |
| TC35 | Security &amp; database | test_TC35_authenticated_actor_can_work_with_preview_disabled | ✅ PASSED | 0.135 |
| TC35 | Story 10 | test_TC35_search_account_id_username_name_and_blank[   ] | ✅ PASSED | 0.439 |
| TC35 | Story 10 | test_TC35_search_account_id_username_name_and_blank[202] | ✅ PASSED | 0.452 |
| TC35 | Story 10 | test_TC35_search_account_id_username_name_and_blank[Name customer1] | ✅ PASSED | 0.479 |
| TC35 | Story 10 | test_TC35_search_account_id_username_name_and_blank[] | ✅ PASSED | 0.453 |
| TC35 | Story 10 | test_TC35_search_account_id_username_name_and_blank[cUsToMeR1] | ✅ PASSED | 0.475 |
| TC36 | Security &amp; database | test_TC36_modifying_posts_require_csrf[create] | ✅ PASSED | 0.082 |
| TC36 | Security &amp; database | test_TC36_modifying_posts_require_csrf[suspend] | ✅ PASSED | 0.088 |
| TC36 | Security &amp; database | test_TC36_modifying_posts_require_csrf[update] | ✅ PASSED | 0.084 |
| TC36 | Story 10 | test_TC36_no_matching_account_has_empty_message | ✅ PASSED | 0.613 |
| TC37 | Security &amp; database | test_TC37_modifying_posts_require_permissions_even_with_valid_csrf[create] | ✅ PASSED | 0.144 |
| TC37 | Security &amp; database | test_TC37_modifying_posts_require_permissions_even_with_valid_csrf[suspend] | ✅ PASSED | 0.156 |
| TC37 | Security &amp; database | test_TC37_modifying_posts_require_permissions_even_with_valid_csrf[update] | ✅ PASSED | 0.131 |
| TC37 | Story 11 | test_TC37_valid_admin_login_opens_dashboard | ✅ PASSED | 0.919 |
| TC38 | Security &amp; database | test_TC38_controller_also_rejects_unauthorized_calls | ✅ PASSED | 0.060 |
| TC39 | Security &amp; database | test_TC39_legacy_upgrade_preserves_profile_and_adds_status[user_profile] | ✅ PASSED | 0.078 |
| TC39 | Security &amp; database | test_TC39_legacy_upgrade_preserves_profile_and_adds_status[user_profiles] | ✅ PASSED | 0.086 |
| TC39 | Story 12 | test_TC39_logout_revokes_current_cookie_and_keeps_other_login | ✅ PASSED | 0.618 |
| TC40 | Security &amp; database | test_TC40_upgrade_stops_for_duplicate_names_without_deleting_rows | ✅ PASSED | 0.051 |
| TC41 | Security &amp; database | test_TC41_upgrade_rejects_unknown_schema_without_deleting_table | ✅ PASSED | 0.055 |
| TC42 | Security &amp; database | test_TC42_ambiguous_existing_account_schema_blocks_suspension | ✅ PASSED | 0.152 |
| TC43 | Security &amp; database | test_TC43_permission_storage_type_matches_database_and_round_trips | ✅ PASSED | 0.048 |
| TC44 | Security &amp; database | test_TC44_unsupported_directory_operation_is_rejected | ✅ PASSED | 0.143 |
| TC67 | Security &amp; database | test_TC67_account_pages_require_their_permission[create] | ✅ PASSED | 0.563 |
| TC67 | Security &amp; database | test_TC67_account_pages_require_their_permission[search] | ✅ PASSED | 0.453 |
| TC67 | Security &amp; database | test_TC67_account_pages_require_their_permission[suspend] | ✅ PASSED | 0.435 |
| TC67 | Security &amp; database | test_TC67_account_pages_require_their_permission[update] | ✅ PASSED | 0.457 |
| TC67 | Security &amp; database | test_TC67_account_pages_require_their_permission[view] | ✅ PASSED | 0.517 |
| TC68 | Security &amp; database | test_TC68_account_modifications_require_csrf[create] | ✅ PASSED | 0.651 |
| TC68 | Security &amp; database | test_TC68_account_modifications_require_csrf[suspend] | ✅ PASSED | 0.520 |
| TC68 | Security &amp; database | test_TC68_account_modifications_require_csrf[update] | ✅ PASSED | 0.456 |
| TC69 | Security &amp; database | test_TC69_last_admin_cannot_lose_access_via_profile_update[remove_permission] | ✅ PASSED | 0.513 |
| TC69 | Security &amp; database | test_TC69_last_admin_cannot_lose_access_via_profile_update[rename] | ✅ PASSED | 0.489 |
| TC69 | Security &amp; database | test_TC69_last_admin_cannot_lose_access_via_profile_update[suspend] | ✅ PASSED | 0.667 |
| TC70 | Story 6 | test_TC70_account_sequence_is_shared_across_profiles | ✅ PASSED | 0.499 |
| TC71 | Story 6 | test_TC71_prefix_uses_actual_multi_digit_profile_id | ✅ PASSED | 0.442 |
| TC72 | Story 6 | test_TC72_existing_accounts_and_legacy_counters_are_preserved | ✅ PASSED | 0.181 |
| TC73 | Story 6 | test_TC73_existing_numeric_id_collision_is_skipped | ✅ PASSED | 0.678 |
| TC74 | Story 6 | test_TC74_account_numbers_can_grow_beyond_two_digits | ✅ PASSED | 0.547 |
| TC75 | Story 6 | test_TC75_failed_creation_rolls_back_account_number | ✅ PASSED | 0.552 |
| TC76 | Story 6 | test_TC76_concurrent_creations_allocate_distinct_shared_numbers | ✅ PASSED | 0.535 |
| TC77 | Story 6 | test_TC77_create_form_has_details_and_no_password_fields | ✅ PASSED | 0.449 |
| TC78 | Story 6 | test_TC78_password_free_admin_cannot_sign_in_until_password_is_set | ✅ PASSED | 0.732 |
| TC79 | Story 6 | test_TC79_submitted_password_fields_cannot_set_credentials | ✅ PASSED | 0.547 |
| TC80 | Story 6 | test_TC80_admin_without_password_cannot_replace_last_usable_admin | ✅ PASSED | 0.452 |
| TC81 | Story 6 | test_TC81_setting_password_enables_login_and_provides_another_usable_admin | ✅ PASSED | 0.867 |
| Collection/setup | Story 11 | test_T38_invalid_or_unavailable_admin_login_is_generic[nonadmin] | ✅ PASSED | 1.156 |
| Collection/setup | Story 11 | test_T38_invalid_or_unavailable_admin_login_is_generic[password] | ✅ PASSED | 2.021 |
| Collection/setup | Story 11 | test_T38_invalid_or_unavailable_admin_login_is_generic[suspended-account] | ✅ PASSED | 0.782 |
| Collection/setup | Story 11 | test_T38_invalid_or_unavailable_admin_login_is_generic[suspended-profile] | ✅ PASSED | 0.812 |
| Collection/setup | Story 11 | test_T38_invalid_or_unavailable_admin_login_is_generic[username] | ✅ PASSED | 1.365 |

Download the job’s report artifact and open `test-results.html` for filters and assertion details, or `coverage/index.html` for executed code lines.

Parameterized tests have one row per input. Skipped tests are not passes. Coverage is a separate measurement from test success.
