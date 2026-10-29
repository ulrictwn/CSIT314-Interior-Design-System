from control.base import Controller
from entity.profile.user_profile import UserProfile


class SuspendUserProfileController(Controller):
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        self.require('profile.suspend')
        return UserProfile.getUserProfile(profileId)

    def suspendUserProfile(self, profileId: int) -> bool:
        self.require('profile.suspend')
        profile = UserProfile()
        suspended = profile.suspendUserProfile(profileId)
        self.error_message = profile.error_message
        self.field_errors = profile.field_errors
        self.error_reason = profile.error_reason
        return suspended
