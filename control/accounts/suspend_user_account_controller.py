# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class SuspendUserAccountController:
    def __init__(self):
        """Create the UserAccount operation object from entity/accounts/user_account.py."""
        self.entity = UserAccount()

    def suspendUserAccount(self, accountId: str) -> bool:
        """Relay suspendUserAccount to UserAccount from entity/accounts/user_account.py."""
        return self.entity.suspendUserAccount(accountId)
