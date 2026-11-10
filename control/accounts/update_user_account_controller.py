# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class UpdateUserAccountController:
    def __init__(self):
        """Create the UserAccount operation object from entity/accounts/user_account.py."""
        self.entity = UserAccount()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        """Relay updateUserAccount to UserAccount from entity/accounts/user_account.py."""
        return self.entity.updateUserAccount(accountId, fullName, email, profileId)
