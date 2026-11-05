from entity.accounts.user_account import UserAccount


class ViewUserAccountController:
    def getUserAccount(self, accountId: str) -> UserAccount | None:
        return UserAccount.getUserAccount(accountId)
