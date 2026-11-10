# entity/company/company_profile.py: company records and database operations.
from entity.company.company_profile import CompanyProfile


class ViewCompanyProfileController:

    def getCompanyProfile(self, accountId: str) -> CompanyProfile | None:
        """Relay this request to the imported CompanyProfile entity and return its result."""
        return CompanyProfile.getCompanyProfile(accountId)
