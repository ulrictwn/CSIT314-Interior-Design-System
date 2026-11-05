from flask import render_template, request
from flask.views import MethodView
from boundary.profile.create_user_profile_page import CreateUserProfilePage
from boundary.profile.view_user_profile_page import ViewUserProfilePage
from boundary.profile.update_user_profile_page import UpdateUserProfilePage
from boundary.profile.suspend_user_profile_page import SuspendUserProfilePage
from boundary.profile.search_user_profile_page import SearchUserProfilePage
from control.profile.profile_controllers import ProfileDirectoryController
from infrastructure.errors import DomainError


class UserProfilesPage(MethodView):
    def get(self):
        mode = request.args.get('mode', 'view')
        if mode not in ('view', 'update', 'suspend'):
            raise DomainError('Choose a supported profile operation.')
        profiles = ProfileDirectoryController().listForAction()
        return render_template('profiles/index.html', profiles=profiles, mode=mode,
            title=mode.title() + ' User Profiles')
