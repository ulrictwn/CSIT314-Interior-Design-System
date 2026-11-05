"""Form/JSON input and account context for the designer boundaries."""
from flask import request, session
from boundary.validation import valid_account_id
from infrastructure.errors import DomainError


def request_values():
    if request.is_json:
        values = request.get_json(silent=True)
        return values if isinstance(values, dict) else {}
    return request.form


def account_id(explicit=None):
    value = explicit
    if value is None:
        values = request_values()
        if 'accountId' in values:
            value = values.get('accountId')
        elif 'accountId' in request.args:
            value = request.args.get('accountId')
        else:
            value = session.get('account_id')
    if not valid_account_id(value):
        raise DomainError('Provide a valid account ID (at most 32 characters).')
    return value.strip()
