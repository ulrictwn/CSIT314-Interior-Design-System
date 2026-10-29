from control.base import Controller
from entity.accounts.user_account import UserAccount


class ViewUserAccountController(Controller):
    def getUserAccount(self, accountId: str) -> UserAccount | None:
        self.require('account.view')
        return UserAccount.getUserAccount(accountId)
