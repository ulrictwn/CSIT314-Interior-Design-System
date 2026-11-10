"""Boundary error presentation for HTML browsers and JSON clients."""
# boundary/designer/presentation.py: chooses designer HTML/JSON responses.
from boundary.designer.presentation import present


def error_response(message, errors=None, status=400, values=None):
    """Format an error using present() from boundary/designer/presentation.py."""
    response = dict(ok=False, message=message, errors=errors or {})
    if values is not None:
        response['values'] = values
    return present(response, status)


def entity_error(controller, values=None):
    """Read the controller entity's error details and prepare the matching response."""
    status = 404 if controller.entity.error_reason == 'not_found' else 400
    return error_response(controller.entity.error_message, controller.entity.field_errors, status, values)
