import math
from boundary.validation import required_text
from infrastructure.errors import DomainError

PROJECT_FIELDS = ['projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description']


def positive_integer(value, label):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise DomainError(f'{label} must be a positive integer.')
    try:
        number = int(value)
    except ValueError:
        raise DomainError(f'{label} must be a positive integer.') from None
    if not 1 <= number <= 2_147_483_647:
        raise DomainError(f'{label} must be a positive database integer.')
    return number


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


def project_values(project):
    return dict(projectId=project.project_id, accountId=project.account_id,
        projectName=project.project_name, categoryId=project.category_id,
        propertyType=project.property_type, area=project.area,
        renovationCost=project.renovation_cost, description=project.description,
        status=project.project_status)
