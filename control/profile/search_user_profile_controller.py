# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class SearchUserProfileController:
    def searchUserProfiles(self, keyword: str) -> list[UserProfile]:
        """Relay searchUserProfiles to UserProfile from entity/profile/user_profile.py."""
        return UserProfile.searchUserProfiles(keyword)
