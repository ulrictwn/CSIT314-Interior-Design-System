from entity.validation import required_text
from infrastructure.errors import DomainError


def validate_category_fields(categoryName, description):
    values, errors = {}, {}
    for field, value, label, maximum in [('categoryName', categoryName, 'Category name', 100),
                                         ('description', description, 'Description', 10000)]:
        try:
            values[field] = required_text(value, label, maximum)
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors
