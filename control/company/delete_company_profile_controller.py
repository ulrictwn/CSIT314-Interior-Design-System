from entity.company.company_profile import CompanyProfile


class DeleteCompanyProfileController:
    def __init__(self):
        self.entity = CompanyProfile()

    def deleteCompanyProfile(self, accountId: str) -> bool:
        return self.entity.deleteCompanyProfile(accountId)
