from entity.accounts.user_account import UserAccount


class UpdateUserAccountController:
    def __init__(self):
        self.entity = UserAccount()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        return self.entity.updateUserAccount(accountId, fullName, email, profileId)
