from entity.profile.user_profile import UserProfile


class SearchUserProfileController:
    def listUserProfiles(self) -> list[UserProfile]:
        return UserProfile.listUserProfiles()

    def searchUserProfiles(self, keyword: str) -> list[UserProfile]:
        return UserProfile.searchUserProfiles(keyword)
