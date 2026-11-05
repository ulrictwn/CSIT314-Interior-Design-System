from entity.profile.user_profile import UserProfile


class SuspendUserProfileController:
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        return UserProfile.getUserProfile(profileId)

    def suspendUserProfile(self, profileId: int) -> bool:
        profile = UserProfile()
        suspended = profile.suspendUserProfile(profileId)
        self.error_message = profile.error_message
        self.field_errors = profile.field_errors
        self.error_reason = profile.error_reason
        return suspended
