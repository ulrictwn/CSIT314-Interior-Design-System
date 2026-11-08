import math
from entity.validation import required_text, positive_integer
from infrastructure.errors import DomainError



def renovation_cost(value):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise DomainError('Renovation cost must be a non-negative number.') from None
    if isinstance(value, bool) or not math.isfinite(number) or number < 0:
        raise DomainError('Renovation cost must be a finite, non-negative number.')
    return number


def validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description):
    values, errors = {}, {}
    validators = {
        'projectName': lambda: required_text(projectName, 'Project name', 150),
        'categoryId': lambda: positive_integer(categoryId, 'Category ID'),
        'propertyType': lambda: required_text(propertyType, 'Property type', 100),
        'area': lambda: required_text(area, 'Area', 100),
        'renovationCost': lambda: renovation_cost(renovationCost),
        'description': lambda: required_text(description, 'Description', 10000),
    }
    for field, validator in validators.items():
        try:
            values[field] = validator()
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors
