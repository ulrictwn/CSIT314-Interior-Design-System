"""Boundary input cleanup and field checks shared by the story event handlers."""
# infrastructure/validation.py: provides shared pure field/value checks.
from infrastructure.validation import (
    password_value, validate_profile_fields, valid_account_id,
    validate_account_details, validate_login_credentials, validate_account_fields,
    search_text, positive_integer, validate_company_fields,
    validate_project_fields, validate_category_fields, validate_report_dates,
)


def strip_input(value):
    """Trim ordinary text before the shared input checks; leave passwords untouched at their call sites."""
    return value.strip() if isinstance(value, str) else value
