from entity.accounts.user_account import UserAccount


class SearchUserAccountController:
    def searchUserAccounts(self, keyword: str = '') -> list[UserAccount]:
        return UserAccount.searchUserAccounts(keyword)
