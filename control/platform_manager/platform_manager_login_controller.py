# entity/accounts/user_account.py: saved account data and credential checks.
from entity.accounts.user_account import UserAccount


class PlatformManagerLoginController:
    def __init__(self):
        """Create the UserAccount entity used to check saved credentials."""
        self.entity = UserAccount()

    def login(self, username: str, password: str) -> bool:
        """Pass the request to UserAccount.login and return its result."""
        return self.entity.login(username, password, 'Platform Manager')
