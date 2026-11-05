from control.profile.create_user_profile_controller import CreateUserProfileController
from control.profile.view_user_profile_controller import ViewUserProfileController
from control.profile.update_user_profile_controller import UpdateUserProfileController
from control.profile.suspend_user_profile_controller import SuspendUserProfileController
from control.profile.search_user_profile_controller import SearchUserProfileController
from entity.profile.user_profile import UserProfile


class ProfileDirectoryController:
    def listForAction(self):
        return UserProfile.listUserProfiles()
