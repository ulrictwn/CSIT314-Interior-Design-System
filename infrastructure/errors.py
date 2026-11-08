class DomainError(ValueError):
    """An expected business-rule failure that can be shown to the user."""


class NotFoundError(DomainError):
    pass


class AccessDeniedError(DomainError):
    """The signed-in account cannot access this portal or record."""
