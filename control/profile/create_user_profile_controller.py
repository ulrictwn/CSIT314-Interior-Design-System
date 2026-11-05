from entity.profile.user_profile import UserProfile
from infrastructure.permissions import PERMISSION_OPTIONS


class CreateUserProfileController:
    PERMISSION_OPTIONS = PERMISSION_OPTIONS

    def userProfileExists(self, profileName: str) -> bool:
        return UserProfile.userProfileExists(profileName)

    def createUserProfile(self, profileName: str, description: str, status: bool,
                          permissions: list[str]) -> bool:
        profile = UserProfile()
        created = profile.createUserProfile(profileName, description, status, permissions)
        self.error_message = profile.error_message
        self.field_errors = profile.field_errors
        return created
