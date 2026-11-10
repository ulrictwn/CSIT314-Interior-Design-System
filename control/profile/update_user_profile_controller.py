# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class UpdateUserProfileController:
    def __init__(self):
        """Create the UserProfile operation object from entity/profile/user_profile.py."""
        self.entity = UserProfile()

    def getUserProfile(self, profileId: int) -> UserProfile | None:
        """Relay getUserProfile to UserProfile from entity/profile/user_profile.py."""
        return UserProfile.getUserProfile(profileId)

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str]) -> bool:
        """Relay updateUserProfile to UserProfile from entity/profile/user_profile.py."""
        return self.entity.updateUserProfile(profileId, profileName, description, permissions)
