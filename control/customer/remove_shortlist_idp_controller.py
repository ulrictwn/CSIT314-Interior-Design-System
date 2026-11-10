# entity/shortlist/shortlist.py: saved customer/project relationships.
from entity.shortlist.shortlist import Shortlist


class RemoveShortlistIDPController:
    def __init__(self):
        """Create the Shortlist operation entity used by this controller."""
        self.entity = Shortlist()

    def removeShortlist(self, accountId: str, projectId: int) -> bool:
        """Pass the request to Shortlist.removeShortlist and return its result."""
        return self.entity.removeShortlist(accountId, projectId)
