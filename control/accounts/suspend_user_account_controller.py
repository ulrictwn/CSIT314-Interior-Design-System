from entity.accounts.user_account import UserAccount


class SuspendUserAccountController:
    def __init__(self):
        self.entity = UserAccount()

    def suspendUserAccount(self, accountId: str) -> bool:
        return self.entity.suspendUserAccount(accountId)
