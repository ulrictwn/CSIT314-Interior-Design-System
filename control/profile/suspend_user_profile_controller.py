from entity.profile.user_profile import UserProfile


class SuspendUserProfileController:
    def __init__(self):
        self.entity = UserProfile()

    def suspendUserProfile(self, profileId: int) -> bool:
        return self.entity.suspendUserProfile(profileId)
