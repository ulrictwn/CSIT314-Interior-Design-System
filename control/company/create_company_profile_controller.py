from entity.company.company_profile import CompanyProfile


class CreateCompanyProfileController:
    def createCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str, companyRegistrationNumber: str) -> bool:
        profile = CompanyProfile()
        result = profile.createCompanyProfile(accountId, companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        self.error_message, self.field_errors = profile.error_message, profile.field_errors
        self.error_reason = profile.error_reason
        self.profile = profile if result else None
        return result
