from control.base import Controller
from entity.profile.user_profile import UserProfile


class UpdateUserProfileController(Controller):
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        self.require('profile.update')
        return UserProfile.getUserProfile(profileId)

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str], status: bool | None = None) -> bool:
        self.require('profile.update')
        profile = UserProfile()
        updated = profile.updateUserProfile(profileId, profileName, description, permissions, status)
        self.error_message = profile.error_message
        self.field_errors = profile.field_errors
        self.error_reason = profile.error_reason
        return updated
