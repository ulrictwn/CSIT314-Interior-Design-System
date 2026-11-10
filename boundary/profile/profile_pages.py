from flask import render_template, request
from flask.views import MethodView
# Controller used to relay this boundary request from control/profile/search_user_profile_controller.py.
from control.profile.search_user_profile_controller import SearchUserProfileController
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError


class UserProfilesPage(MethodView):
    def get(self):
        """Display profiles with the selected view, update or suspend action.

        Uses control/profile/search_user_profile_controller.py.
        """
        mode = request.args.get('mode', 'view')
        if mode not in ('view', 'update', 'suspend'):
            raise DomainError('Choose a supported profile operation.')
        profiles = SearchUserProfileController().searchUserProfiles('')
        return render_template('profiles/index.html', profiles=profiles, mode=mode,
            title=mode.title() + ' User Profiles')
