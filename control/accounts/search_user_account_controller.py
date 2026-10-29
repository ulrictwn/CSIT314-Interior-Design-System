from control.base import Controller
from entity.accounts.user_account import UserAccount


class SearchUserAccountController(Controller):
    def searchUserAccounts(self, keyword: str = '') -> list[UserAccount]:
        self.require('account.search')
        return UserAccount.searchUserAccounts(keyword)
