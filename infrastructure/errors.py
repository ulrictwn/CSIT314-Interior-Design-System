class DomainError(ValueError):
    """An expected business-rule failure that can be shown to the user."""


class NotFoundError(DomainError):
    pass
