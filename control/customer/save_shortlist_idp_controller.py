from entity.shortlist.shortlist import Shortlist


class SaveShortlistIDPController:
    def __init__(self):
        self.entity = Shortlist()

    def saveShortlist(self, accountId: str, projectId: int) -> bool:
        return self.entity.saveShortlist(accountId, projectId)
