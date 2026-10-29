from flask import render_template, request
from boundary.base import Page
from boundary.profile.create_user_profile_page import CreateUserProfilePage
from boundary.profile.view_user_profile_page import ViewUserProfilePage
from boundary.profile.update_user_profile_page import UpdateUserProfilePage
from boundary.profile.suspend_user_profile_page import SuspendUserProfilePage
from boundary.profile.search_user_profile_page import SearchUserProfilePage
from control.profile.profile_controllers import ProfileDirectoryController
from infrastructure.errors import AccessError


class UserProfilesPage(Page):
    def get(self):
        if not any(self.actor.has_permission(f'profile.{action}') for action in ('create', 'view', 'update', 'suspend', 'search')):
            raise AccessError('You do not have permission to access user profiles.')
        mode = request.args.get('mode', 'view')
        if mode == 'view' and not self.actor.has_permission('profile.view'):
            return render_template('profiles/index.html', profiles=None, mode=mode, title='User Profiles')
        profiles = ProfileDirectoryController(self.actor).listForAction(mode)
        return render_template('profiles/index.html', profiles=profiles, mode=mode,
                               title={'view': 'View', 'update': 'Update', 'suspend': 'Suspend'}.get(mode, 'View') + ' User Profiles')
