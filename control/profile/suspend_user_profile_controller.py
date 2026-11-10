# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class SuspendUserProfileController:
    def __init__(self):
        """Create the UserProfile operation object from entity/profile/user_profile.py."""
        self.entity = UserProfile()

    def suspendUserProfile(self, profileId: int) -> bool:
        """Relay suspendUserProfile to UserProfile from entity/profile/user_profile.py."""
        return self.entity.suspendUserProfile(profileId)
