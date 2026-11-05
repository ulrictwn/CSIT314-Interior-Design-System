from entity.company.company_profile import CompanyProfile


class ViewCompanyProfileController:

    def getCompanyProfile(self, accountId: str) -> CompanyProfile | None:
        return CompanyProfile.getCompanyProfile(accountId)
