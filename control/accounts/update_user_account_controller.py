from control.base import Controller
from entity.accounts.user_account import UserAccount


class UpdateUserAccountController(Controller):
    def getUserAccount(self, accountId: str) -> UserAccount | None:
        self.require('account.update')
        return UserAccount.getUserAccount(accountId)

    def activeProfiles(self):
        self.require('account.update')
        return UserAccount.activeProfiles()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        self.require('account.update')
        account = UserAccount()
        updated = account.updateUserAccount(accountId, fullName, email, profileId)
        self.error_message = account.error_message
        self.field_errors = account.field_errors
        self.error_reason = account.error_reason
        return updated
