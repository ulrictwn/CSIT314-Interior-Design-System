from entity.validation import required_text, email_address, phone_number_value
from infrastructure.errors import DomainError



def validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber):
    values, errors = {}, {}
    validators = {
        'companyName': lambda: required_text(companyName, 'Company name', 150),
        'companyContact': lambda: phone_number_value(companyContact),
        'companyAddress': lambda: required_text(companyAddress, 'Company address', 1000),
        'companyEmail': lambda: email_address(companyEmail),
        'companyRegistrationNumber': lambda: required_text(companyRegistrationNumber, 'Business registration number', 100),
    }
    for field, validator in validators.items():
        try:
            values[field] = validator()
        except DomainError as error:
            errors[field] = [str(error)]
    return values, errors
