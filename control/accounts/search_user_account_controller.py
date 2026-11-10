# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class SearchUserAccountController:
    def searchUserAccounts(self, keyword: str = '') -> list[UserAccount]:
        """Relay searchUserAccounts to UserAccount from entity/accounts/user_account.py."""
        return UserAccount.searchUserAccounts(keyword)
