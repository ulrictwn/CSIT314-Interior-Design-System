from entity.profile.user_profile import UserProfile


class ProfileDirectoryController:
    def listForAction(self):
        return UserProfile.listUserProfiles()

    def activeProfiles(self):
        return UserProfile.activeProfiles()
