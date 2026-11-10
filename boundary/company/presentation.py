COMPANY_FIELDS = ['companyName', 'companyContact', 'companyAddress', 'companyEmail', 'companyRegistrationNumber']


def company_values(profile):
    """Prepare the company fields used by HTML and JSON displays."""
    return dict(accountId=profile.account_id, companyName=profile.company_name,
        companyContact=profile.company_contact, companyAddress=profile.company_address,
        companyEmail=profile.company_email, companyRegistrationNumber=profile.company_registration_number)
