from entity.shortlist.shortlist import Shortlist


class ViewShortlistCountController:
    def getShortlistCount(self, projectId: int) -> int:
        return Shortlist.getShortlistCount(projectId)
