from entity.profile.user_profile import UserProfile
from entity.accounts.user_account import UserAccount


class CreateUserAccountController:
    def __init__(self):
        self.entity = UserAccount()

    def activeProfiles(self):
        return UserProfile.activeProfiles()

    def userAccountExists(self, username: str) -> bool:
        return UserAccount.userAccountExists(username)

    def createUserAccount(self, username: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int) -> bool:
        return self.entity.createUserAccount(username, fullName, email, phoneNumber, profileId)
