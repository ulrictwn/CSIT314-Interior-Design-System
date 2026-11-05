from entity.company.company_profile import CompanyProfile


class DeleteCompanyProfileController:
    def deleteCompanyProfile(self, accountId: str) -> bool:
        profile = CompanyProfile()
        result = profile.deleteCompanyProfile(accountId)
        self.error_message, self.field_errors = profile.error_message, profile.field_errors
        self.error_reason = profile.error_reason
        return result

    def getCompanyProfile(self, accountId: str) -> CompanyProfile | None:
        return CompanyProfile.getCompanyProfile(accountId)
