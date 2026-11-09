from entity.accounts.user_account import UserAccount


class CreateUserAccountController:
    def __init__(self):
        self.entity = UserAccount()

    def createUserAccount(self, username: str, password: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int) -> bool:
        return self.entity.createUserAccount(username, password, fullName, email, phoneNumber, profileId)
