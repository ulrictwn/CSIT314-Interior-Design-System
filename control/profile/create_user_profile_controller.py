# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class CreateUserProfileController:
    def __init__(self):
        """Create the UserProfile operation object from entity/profile/user_profile.py."""
        self.entity = UserProfile()

    def createUserProfile(self, profileName: str, description: str, status: str,
                          permissions: list[str]) -> bool:
        """Relay createUserProfile to UserProfile from entity/profile/user_profile.py."""
        return self.entity.createUserProfile(profileName, description, status, permissions)
