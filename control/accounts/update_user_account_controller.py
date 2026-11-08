from entity.profile.user_profile import UserProfile
from entity.accounts.user_account import UserAccount


class UpdateUserAccountController:
    def __init__(self):
        self.entity = UserAccount()

    def getUserAccount(self, accountId: str) -> UserAccount | None:
        return UserAccount.getUserAccount(accountId)

    def activeProfiles(self):
        return UserProfile.activeProfiles()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        return self.entity.updateUserAccount(accountId, fullName, email, profileId)
