# entity/company/company_profile.py: company records and database operations.
from entity.company.company_profile import CompanyProfile


class SearchCompanyProfileController:
    def searchCompanyProfile(self, accountId: str, keyword: str) -> list[str]:
        """Relay this request to the imported CompanyProfile entity and return its result."""
        return CompanyProfile.searchCompanyProfile(accountId, keyword)
