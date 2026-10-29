from control.base import Controller
from control.profile.create_user_profile_controller import CreateUserProfileController
from control.profile.view_user_profile_controller import ViewUserProfileController
from control.profile.update_user_profile_controller import UpdateUserProfileController
from control.profile.suspend_user_profile_controller import SuspendUserProfileController
from control.profile.search_user_profile_controller import SearchUserProfileController
from entity.profile.user_profile import UserProfile
from infrastructure.errors import DomainError


class ProfileDirectoryController(Controller):
    def listForAction(self, mode='view'):
        permission = {'view': 'profile.view', 'update': 'profile.update', 'suspend': 'profile.suspend'}.get(mode)
        if permission is None:
            raise DomainError('Choose a supported profile operation.')
        self.require(permission)
        return UserProfile.listUserProfiles()
