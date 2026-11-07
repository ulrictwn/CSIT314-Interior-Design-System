from entity.shortlist.shortlist import Shortlist


class SaveShortlistIDPController:
    def saveShortlist(self, accountId: str, projectId: int) -> bool:
        entity = Shortlist()
        result = entity.saveShortlist(accountId, projectId)
        self.error_message, self.field_errors, self.error_reason = entity.error_message, entity.field_errors, entity.error_reason
        return result
