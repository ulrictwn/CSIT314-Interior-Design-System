from entity.company.company_profile import CompanyProfile


class SearchCompanyProfileController:
    def searchCompanyProfile(self, accountId: str, keyword: str) -> list[str]:
        return CompanyProfile.searchCompanyProfile(accountId, keyword)
