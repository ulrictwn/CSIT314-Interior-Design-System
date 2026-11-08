"""Field and format validation used by entity operations and trusted CLI commands."""
import re
from email_validator import validate_email, EmailNotValidError
from infrastructure.errors import DomainError
from infrastructure.permissions import PERMISSION_OPTIONS


def required_text(value, label, maximum=10000):
    if not isinstance(value, str) or not value.strip():
        raise DomainError(f'{label} is required.')
    value = value.strip()
    if len(value) > maximum:
        raise DomainError(f'{label} must be at most {maximum} characters.')
    return value


def username_value(value):
    value = required_text(value, 'Username', 80)
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,80}', value):
        raise DomainError('Username must contain 3–80 letters, numbers, dots, underscores, or hyphens.')
    return value


def email_address(value):
    try:
        return validate_email(required_text(value, 'Email', 254), check_deliverability=False).normalized.lower()
    except EmailNotValidError as error:
        raise DomainError('Enter a valid email address.') from error


def phone_number_value(value):
    value = required_text(value, 'Phone number', 40)
    if not re.fullmatch(r'\+?[0-9][0-9 ()-]{5,38}', value):
        raise DomainError('Enter a valid phone number.')
    return value


def password_value(value):
    if not isinstance(value, str) or not 12 <= len(value) <= 128:
        raise DomainError('Passwords must contain between 12 and 128 characters.')
    return value


def validate_profile_fields(profileName, description, status, permissions):
    """Collect field errors and normalize data without database access."""
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
    return type(profileId) is int and 1 <= profileId <= 2_147_483_647


def valid_account_id(accountId):
    return isinstance(accountId, str) and bool(accountId.strip()) and len(accountId) <= 32


def validate_account_details(fullName, email, profileId):
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
    """Apply the existing required-field and length rules before database access."""
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
    if not isinstance(keyword, str):
        raise DomainError('Search text must contain at most 200 characters.')
    if required and not keyword.strip():
        raise DomainError('Search text is required.')
    if len(keyword.strip()) > 200:
        raise DomainError('Search text must be at most 200 characters.')
    return keyword.strip()


def positive_integer(value, label):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise DomainError(f'{label} must be a positive integer.')
    try:
        number = int(value)
    except ValueError:
        raise DomainError(f'{label} must be a positive integer.') from None
    if not 1 <= number <= 2_147_483_647:
        raise DomainError(f'{label} must be a positive database integer.')
    return number

