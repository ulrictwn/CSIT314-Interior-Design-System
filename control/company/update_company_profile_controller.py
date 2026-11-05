from entity.company.company_profile import CompanyProfile


class UpdateCompanyProfileController:
    def updateCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str, companyRegistrationNumber: str) -> bool:
        profile = CompanyProfile()
        result = profile.updateCompanyProfile(accountId, companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        self.error_message, self.field_errors = profile.error_message, profile.field_errors
        self.error_reason = profile.error_reason
        return result

    def getCompanyProfile(self, accountId: str) -> CompanyProfile | None:
        return CompanyProfile.getCompanyProfile(accountId)
