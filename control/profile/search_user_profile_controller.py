from entity.profile.user_profile import UserProfile


class SearchUserProfileController:
    def searchUserProfiles(self, keyword: str) -> list[UserProfile]:
        return UserProfile.searchUserProfiles(keyword)
