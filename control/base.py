from infrastructure.errors import AccessError, DomainError


class Controller:
    def __init__(self, actor=None):
        self.actor = actor

    def require(self, permission):
        if self.actor is None or not self.actor.has_permission(permission):
            raise AccessError('An authorized User Admin is required for this action.')


def required(value, label, maximum=10000):
    if not isinstance(value, str) or not value.strip():
        raise DomainError(f'{label} is required.')
    value = value.strip()
    if len(value) > maximum:
        raise DomainError(f'{label} must be at most {maximum} characters.')
    return value
