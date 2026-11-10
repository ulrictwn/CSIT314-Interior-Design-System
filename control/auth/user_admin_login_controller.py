# entity/accounts/user_account.py: provides the saved-data entity used by this operation.
from entity.accounts.user_account import UserAccount


class UserAdminLoginController:
    def __init__(self):
        """Create the UserAccount operation object imported from entity/accounts/user_account.py."""
        self.entity = UserAccount()

    def login(self, username: str, password: str) -> bool:
        """Pass the credentials and User Admin role to the imported UserAccount.login()."""
        return self.entity.login(username, password, 'User Admin')
