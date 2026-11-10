# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class CreateUserAccountController:
    def __init__(self):
        """Create the UserAccount operation object from entity/accounts/user_account.py."""
        self.entity = UserAccount()

    def createUserAccount(self, username: str, password: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int) -> bool:
        """Relay createUserAccount to UserAccount from entity/accounts/user_account.py."""
        return self.entity.createUserAccount(username, password, fullName, email, phoneNumber, profileId)
