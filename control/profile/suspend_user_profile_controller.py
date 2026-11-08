from entity.profile.user_profile import UserProfile


class SuspendUserProfileController:
    def __init__(self):
        self.entity = UserProfile()

    def getUserProfile(self, profileId: int) -> UserProfile | None:
        return UserProfile.getUserProfile(profileId)

    def suspendUserProfile(self, profileId: int) -> bool:
        return self.entity.suspendUserProfile(profileId)
