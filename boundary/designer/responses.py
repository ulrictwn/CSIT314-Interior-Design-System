"""Boundary error presentation for HTML browsers and JSON clients."""
from boundary.designer.presentation import present


def error_response(message, errors=None, status=400, values=None):
    response = dict(ok=False, message=message, errors=errors or {})
    if values is not None:
        response['values'] = values
    return present(response, status)


def entity_error(controller, values=None):
    status = 404 if controller.error_reason == 'not_found' else 400
    return error_response(controller.error_message, controller.field_errors, status, values)
