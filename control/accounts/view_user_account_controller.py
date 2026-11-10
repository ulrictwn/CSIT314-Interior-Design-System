# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class ViewUserAccountController:
    def getUserAccount(self, accountId: str) -> UserAccount | None:
        """Relay getUserAccount to UserAccount from entity/accounts/user_account.py."""
        return UserAccount.getUserAccount(accountId)
