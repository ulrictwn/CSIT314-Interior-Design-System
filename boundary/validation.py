"""Boundary text cleanup only; entity operations validate all submitted values."""


def strip_input(value):
    """Trim ordinary text while leaving malformed values for entity validation."""
    return value.strip() if isinstance(value, str) else value
