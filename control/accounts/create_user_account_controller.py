from entity.accounts.user_account import UserAccount


class CreateUserAccountController:
    def activeProfiles(self):
        return UserAccount.activeProfiles()

    def userAccountExists(self, username: str) -> bool:
        return UserAccount.userAccountExists(username)

    def createUserAccount(self, username: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int) -> bool:
        account = UserAccount()
        created = account.createUserAccount(username, fullName, email, phoneNumber, profileId)
        self.error_message = account.error_message
        self.field_errors = account.field_errors
        self.error_reason = account.error_reason
        return created
