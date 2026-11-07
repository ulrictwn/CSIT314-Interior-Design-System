from entity.shortlist.shortlist import Shortlist


class CustomerDashboardController:
    def summary(self, accountId):
        return Shortlist.dashboard(accountId)

    def savedProjectIds(self, accountId):
        return Shortlist.savedProjectIds(accountId)
