from entity.shortlist.shortlist import Shortlist


class RemoveShortlistIDPController:
    def __init__(self):
        self.entity = Shortlist()

    def removeShortlist(self, accountId: str, projectId: int) -> bool:
        return self.entity.removeShortlist(accountId, projectId)
