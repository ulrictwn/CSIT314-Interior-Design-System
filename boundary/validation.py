"""HTTP input cleanup only. Entity operations own validation."""


def strip_input(value):
    """Trim ordinary text while leaving non-text values for entity validation."""
    return value.strip() if isinstance(value, str) else value
