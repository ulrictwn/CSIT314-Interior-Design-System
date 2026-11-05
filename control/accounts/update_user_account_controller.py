from entity.accounts.user_account import UserAccount


class UpdateUserAccountController:
    def getUserAccount(self, accountId: str) -> UserAccount | None:
        return UserAccount.getUserAccount(accountId)

    def activeProfiles(self):
        return UserAccount.activeProfiles()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        account = UserAccount()
        updated = account.updateUserAccount(accountId, fullName, email, profileId)
        self.error_message = account.error_message
        self.field_errors = account.field_errors
        self.error_reason = account.error_reason
        return updated
