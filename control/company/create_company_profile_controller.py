from entity.company.company_profile import CompanyProfile


class CreateCompanyProfileController:
    def __init__(self):
        self.entity = CompanyProfile()

    def createCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str, companyRegistrationNumber: str) -> bool:
        return self.entity.createCompanyProfile(accountId, companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
