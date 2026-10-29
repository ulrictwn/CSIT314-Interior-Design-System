from control.base import Controller
from entity.accounts.user_account import UserAccount


class CreateUserAccountController(Controller):
    def activeProfiles(self):
        self.require('account.create')
        return UserAccount.activeProfiles()

    def userAccountExists(self, username: str) -> bool:
        self.require('account.create')
        return UserAccount.userAccountExists(username)

    def createUserAccount(self, username: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int) -> bool:
        self.require('account.create')
        account = UserAccount()
        created = account.createUserAccount(username, fullName, email, phoneNumber, profileId)
        self.error_message = account.error_message
        self.field_errors = account.field_errors
        self.error_reason = account.error_reason
        return created
