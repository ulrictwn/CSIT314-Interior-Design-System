from control.base import Controller
from entity.profile.user_profile import UserProfile


class ViewUserProfileController(Controller):
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        self.require('profile.view')
        return UserProfile.getUserProfile(profileId)
