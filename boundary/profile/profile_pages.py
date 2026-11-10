# Controller used to relay directory reads from control/profile/view_user_profile_controller.py.
from control.profile.view_user_profile_controller import ViewUserProfileController
from flask import render_template, request
from flask.views import MethodView
# Ordinary input cleanup for the directory display option.
from boundary.validation import strip_input


class UserProfilesPage(MethodView):
    def get(self):
        """Display profiles with the selected view, update or suspend action.

        Uses control/profile/view_user_profile_controller.py.
        """
        mode = {'view': 'view', 'update': 'update', 'suspend': 'suspend'}.get(
            strip_input(request.args.get('mode', 'view')), 'view')
        profiles = ViewUserProfileController().listUserProfiles()
        return render_template('profiles/index.html', profiles=profiles, mode=mode,
            title=mode.title() + ' User Profiles')
