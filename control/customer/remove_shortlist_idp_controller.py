from entity.shortlist.shortlist import Shortlist


class RemoveShortlistIDPController:
    def removeShortlist(self, accountId: str, projectId: int) -> bool:
        entity = Shortlist()
        result = entity.removeShortlist(accountId, projectId)
        self.error_message, self.field_errors, self.error_reason = entity.error_message, entity.field_errors, entity.error_reason
        return result
