"""Pure value checks reused by boundaries, entity integrity guards and trusted setup.

Boundary events run field checks before controllers. These helpers perform no
database queries and have no Flask or entity-model dependencies.
"""
import re
import math
from calendar import monthrange
from datetime import date, timedelta
from email_validator import validate_email, EmailNotValidError
# infrastructure/errors.py: defines expected validation, missing-record and access errors.
from infrastructure.errors import DomainError
# infrastructure/permissions.py: defines display labels and supported permission choices.
from infrastructure.permissions import PERMISSION_OPTIONS


def required_text(value, label, maximum=10000):
    """Require nonempty text, trim it and enforce its maximum length."""
    if not isinstance(value, str) or not value.strip():
        raise DomainError(f'{label} is required.')
    value = value.strip()
    if len(value) > maximum:
        raise DomainError(f'{label} must be at most {maximum} characters.')
    return value


def username_value(value):
    """Check the supported username length and characters."""
    value = required_text(value, 'Username', 80)
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,80}', value):
        raise DomainError('Username must contain 3–80 letters, numbers, dots, underscores, or hyphens.')
    return value


def email_address(value):
    """Validate and normalize an email with the email_validator package."""
    try:
        return validate_email(required_text(value, 'Email', 254), check_deliverability=False).normalized.lower()
    except EmailNotValidError as error:
        raise DomainError('Enter a valid email address.') from error


def phone_number_value(value):
    """Check the required phone number length and supported characters."""
    value = required_text(value, 'Phone number', 40)
    if not re.fullmatch(r'\+?[0-9][0-9 ()-]{5,38}', value):
        raise DomainError('Enter a valid phone number.')
    return value


def password_value(value):
    """Check a private setup/reset password's length without trimming it."""
    if not isinstance(value, str) or not 12 <= len(value) <= 128:
        raise DomainError('Passwords must contain between 12 and 128 characters.')
    return value


def validate_profile_fields(profileName, description, status, permissions):
    """Collect profile field errors and normalize the supported status and permission choices."""
    errors = {}
    values = []
    for field, value, label, maximum in (
            ('profileName', profileName, 'Profile name', 100),
            ('description', description, 'Description', 10000)):
        if not isinstance(value, str) or not value.strip():
            errors[field] = [f'{label} is required.']
        elif len(value.strip()) > maximum:
            errors[field] = [f'{label} must be at most {maximum} characters.']
        values.append(value.strip() if isinstance(value, str) else value)
    if not isinstance(status, str) or status.strip() not in ('Active', 'Suspended'):
        errors['status'] = ['Choose Active or Suspended.']
    if not isinstance(permissions, list) or any(
            not isinstance(p, str) or p not in PERMISSION_OPTIONS for p in permissions):
        errors['permissions'] = ['Choose permissions from the supported list.']
    if errors:
        return None, errors
    return (values[0], values[1], status.strip(),
            list(dict.fromkeys(permissions))), {}


def valid_profile_id(profileId):
    """Check that a profile ID is a positive database integer."""
    return type(profileId) is int and 1 <= profileId <= 2_147_483_647


def valid_account_id(accountId):
    """Check that an account ID is nonempty text within the database length."""
    return isinstance(accountId, str) and bool(accountId.strip()) and len(accountId) <= 32


def validate_account_details(fullName, email, profileId):
    """Check the editable full name, email and assigned profile ID."""
    values, errors = {}, {}
    for field, validator in {
        'full_name': lambda: required_text(fullName, 'Full name', 120),
        'email': lambda: email_address(email),
    }.items():
        try:
            values[field] = validator()
        except DomainError as error:
            errors[field] = [str(error)]
    try:
        values['profile_id'] = positive_integer(profileId, 'Profile ID')
    except DomainError:
        errors['profile_id'] = ['Assign an active user profile.']
    return values, errors


def validate_login_credentials(username: str, password: str) -> str:
    """Check required credential fields and lengths while preserving the password exactly."""
    errors = {}
    for field, value, maximum in [('username', username, 80), ('password', password, 128)]:
        if not isinstance(value, str) or not value.strip():
            errors[field] = ['This field is required.']
        elif len(value) > maximum:
            errors[field] = [f'Field cannot be longer than {maximum} characters.']
    if errors:
        error = DomainError('Invalid login details')
        error.field_errors = errors
        raise error
    return username.strip()


def validate_account_fields(username, fullName, email, phoneNumber, profileId):
    """Check account-creation fields and collect errors by form field."""
    values, errors = validate_account_details(fullName, email, profileId)
    for field, validator in {
        'username': lambda: username_value(username),
        'phone_number': lambda: phone_number_value(phoneNumber),
    }.items():
        try:
            values[field] = validator()
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors


def search_text(keyword, *, required=False):
    """Validate and trim a search keyword, requiring text when the caller requests it."""
    if not isinstance(keyword, str):
        raise DomainError('Search text must contain at most 200 characters.')
    if required and not keyword.strip():
        raise DomainError('Search text is required.')
    if len(keyword.strip()) > 200:
        raise DomainError('Search text must be at most 200 characters.')
    return keyword.strip()


def positive_integer(value, label):
    """Convert a submitted ID to a positive database integer and reject unsupported values."""
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise DomainError(f'{label} must be a positive integer.')
    try:
        number = int(value)
    except ValueError:
        raise DomainError(f'{label} must be a positive integer.') from None
    if not 1 <= number <= 2_147_483_647:
        raise DomainError(f'{label} must be a positive database integer.')
    return number


def validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber):
    """Validate company text, contact and email fields without reading the database."""
    values, errors = {}, {}
    validators = {
        'companyName': lambda: required_text(companyName, 'Company name', 150),
        'companyContact': lambda: phone_number_value(companyContact),
        'companyAddress': lambda: required_text(companyAddress, 'Company address', 1000),
        'companyEmail': lambda: email_address(companyEmail),
        'companyRegistrationNumber': lambda: required_text(companyRegistrationNumber, 'Business registration number', 100),
    }
    for field, validator in validators.items():
        try:
            values[field] = validator()
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors


def renovation_cost(value):
    """Convert the cost to a finite non-negative number."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise DomainError('Renovation cost must be a non-negative number.') from None
    if isinstance(value, bool) or not math.isfinite(number) or number < 0:
        raise DomainError('Renovation cost must be a finite, non-negative number.')
    return number


def validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description):
    """Check the six project input fields and collect their individual errors."""
    values, errors = {}, {}
    validators = {
        'projectName': lambda: required_text(projectName, 'Project name', 150),
        'categoryId': lambda: positive_integer(categoryId, 'Category ID'),
        'propertyType': lambda: required_text(propertyType, 'Property type', 100),
        'area': lambda: required_text(area, 'Area', 100),
        'renovationCost': lambda: renovation_cost(renovationCost),
        'description': lambda: required_text(description, 'Description', 10000),
    }
    for field, validator in validators.items():
        try:
            values[field] = validator()
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors


def validate_category_fields(categoryName, description):
    """Check the required category name and description and their lengths."""
    values, errors = {}, {}
    for field, value, label, maximum in [('categoryName', categoryName, 'Category name', 100),
                                         ('description', description, 'Description', 10000)]:
        try:
            values[field] = required_text(value, label, maximum)
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors


def validate_report_dates(kind, startDate, endDate=None):
    """Parse report dates and check the daily, seven-day or calendar-month period."""
    values, errors = {}, {}
    for name, raw in [('startDate',startDate), ('endDate',endDate)]:
        try:
            if name == 'endDate' and raw is None and kind in ('daily', 'weekly') and 'startDate' in values:
                value = values['startDate'] + timedelta(days=6 if kind == 'weekly' else 0)
            elif type(raw) is date:
                value = raw
            elif isinstance(raw, str):
                cleaned = raw.strip()
                value = date.fromisoformat(cleaned)
                if cleaned != value.isoformat():
                    raise ValueError()
            else:
                raise ValueError()
            if not 1900 <= value.year <= 9998:
                raise ValueError()
            values[name] = value
        except (ValueError, TypeError):
            errors[name] = ['Enter a valid date.']
    if errors:
        error = DomainError('Please correct the report dates.')
        error.field_errors = errors
        raise error
    start, end = values['startDate'], values['endDate']
    if kind == 'daily':
        valid = start == end
    elif kind == 'weekly':
        valid = end - start == timedelta(days=6)
    else:
        last_day = monthrange(start.year, start.month)[1]
        valid = start.day == 1 and end == start.replace(day=last_day)
    if not valid:
        message = {'daily':'Choose one day for a daily report.', 'weekly':'Choose seven consecutive days for a weekly report.',
                   'monthly':'Choose the first and last day of one calendar month.'}[kind]
        error = DomainError(message)
        error.field_errors = {'endDate':[message]}
        raise error
    return start,end
