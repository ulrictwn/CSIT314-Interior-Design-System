from entity.company.company_profile import CompanyProfile


class UpdateCompanyProfileController:
    def __init__(self):
        self.entity = CompanyProfile()

    def updateCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str, companyRegistrationNumber: str) -> bool:
        return self.entity.updateCompanyProfile(accountId, companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)

    def getCompanyProfile(self, accountId: str) -> CompanyProfile | None:
        return CompanyProfile.getCompanyProfile(accountId)
