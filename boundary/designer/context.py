"""Read HTTP input and the signed-in account; entity operations validate data."""
from flask import request, session


def request_values():
    if request.is_json:
        values = request.get_json(silent=True)
        return values if isinstance(values, dict) else {}
    return request.form


def account_id(explicit=None):
    return session.get('account_id')
