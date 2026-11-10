# entity/shortlist/shortlist.py: provides the saved-data entity used by this operation.
from entity.shortlist.shortlist import Shortlist


class ViewShortlistCountController:
    def getShortlistCount(self, projectId: int) -> int:
        """Request the saved shortlist count from entity/shortlist/shortlist.py."""
        return Shortlist.getShortlistCount(projectId)
