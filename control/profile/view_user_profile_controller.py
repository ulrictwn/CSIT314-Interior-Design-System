# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class ViewUserProfileController:
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        """Relay getUserProfile to UserProfile from entity/profile/user_profile.py."""
        return UserProfile.getUserProfile(profileId)
