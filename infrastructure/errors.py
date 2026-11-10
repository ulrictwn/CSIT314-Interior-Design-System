class DomainError(ValueError):
    """An expected business-rule failure that can be shown to the user."""


class NotFoundError(DomainError):
    """The requested record does not exist."""


class AccessDeniedError(DomainError):
    """The signed-in account cannot access this portal or record."""
