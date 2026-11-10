"""Read HTTP input and the signed-in account for boundary event handlers."""
from flask import request, session


def request_values():
    """Read a JSON object or form values from the current Flask request."""
    if request.is_json:
        values = request.get_json(silent=True)
        return values if isinstance(values, dict) else {}
    return request.form


def account_id():
    """Read the signed-in account ID from the Flask browser session."""
    return session.get('account_id')
