# entity/company/company_profile.py: company records and database operations.
from entity.company.company_profile import CompanyProfile


class CreateCompanyProfileController:
    def __init__(self):
        """Keep the imported CompanyProfile entity for this operation."""
        self.entity = CompanyProfile()

    def createCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str, companyRegistrationNumber: str) -> bool:
        """Relay this request to the imported CompanyProfile entity and return its result."""
        return self.entity.createCompanyProfile(accountId, companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
