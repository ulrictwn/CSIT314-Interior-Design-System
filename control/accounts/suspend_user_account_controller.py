from entity.accounts.user_account import UserAccount


class SuspendUserAccountController:
    def getUserAccount(self, accountId: str) -> UserAccount | None:
        return UserAccount.getUserAccount(accountId)

    def suspendUserAccount(self, accountId: str) -> bool:
        account = UserAccount()
        suspended = account.suspendUserAccount(accountId)
        self.error_message = account.error_message
        self.field_errors = account.field_errors
        self.error_reason = account.error_reason
        return suspended
