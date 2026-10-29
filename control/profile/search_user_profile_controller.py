from control.base import Controller
from entity.profile.user_profile import UserProfile


class SearchUserProfileController(Controller):
    def listUserProfiles(self) -> list[UserProfile]:
        self.require('profile.search')
        return UserProfile.listUserProfiles()

    def searchUserProfiles(self, keyword: str) -> list[UserProfile]:
        self.require('profile.search')
        return UserProfile.searchUserProfiles(keyword)
