# entity/accounts/user_account.py: validates the selected Staff portal role.
from entity.accounts.user_account import UserAccount


class StaffLoginController:
    def selectRole(self, role):
        """Relay Staff selector validation to the UserAccount entity."""
        return UserAccount.staffRole(role)
