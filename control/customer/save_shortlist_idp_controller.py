# entity/shortlist/shortlist.py: saved customer/project relationships.
from entity.shortlist.shortlist import Shortlist


class SaveShortlistIDPController:
    def __init__(self):
        """Create the Shortlist operation entity used by this controller."""
        self.entity = Shortlist()

    def saveShortlist(self, accountId: str, projectId: int) -> bool:
        """Pass the request to Shortlist.saveShortlist and return its result."""
        return self.entity.saveShortlist(accountId, projectId)
