from entity.accounts.user_account import UserAccount


class StaffLoginController:
    def selectRole(self, role):
        return UserAccount.staffRole(role)
