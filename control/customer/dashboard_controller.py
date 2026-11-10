# entity/shortlist/shortlist.py: saved customer/project relationships.
from entity.shortlist.shortlist import Shortlist


class CustomerDashboardController:
    def summary(self, accountId):
        """Pass the request to Shortlist.dashboard and return its result."""
        return Shortlist.dashboard(accountId)

    def savedProjectIds(self, accountId):
        """Pass the request to Shortlist.savedProjectIds and return its result."""
        return Shortlist.savedProjectIds(accountId)
