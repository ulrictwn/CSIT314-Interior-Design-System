# entity/company/company_profile.py: company records and database operations.
from entity.company.company_profile import CompanyProfile


class DeleteCompanyProfileController:
    def __init__(self):
        """Keep the imported CompanyProfile entity for this operation."""
        self.entity = CompanyProfile()

    def deleteCompanyProfile(self, accountId: str) -> bool:
        """Relay this request to the imported CompanyProfile entity and return its result."""
        return self.entity.deleteCompanyProfile(accountId)
