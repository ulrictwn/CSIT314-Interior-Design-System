# Controller used to relay this boundary request from control/profile/view_user_profile_controller.py.
from control.profile.view_user_profile_controller import ViewUserProfileController
from flask import render_template, redirect, url_for, flash
from flask.views import MethodView
# Input cleanup and field checks from boundary/validation.py.
from boundary.validation import positive_integer, strip_input
# Controller used to relay this boundary request from control/profile/suspend_user_profile_controller.py.
from control.profile.suspend_user_profile_controller import SuspendUserProfileController


class SuspendUserProfilePage(MethodView):

    def get(self, profile_id):
        """Load the selected profile for suspension confirmation.

        Uses boundary/validation.py, control/profile/view_user_profile_controller.py.
        """
        self.profile = ViewUserProfileController().getUserProfile(positive_integer(profile_id, 'Profile ID'))
        if self.profile is None:
            self.error_message, self.error_reason = 'User profile not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template('profiles/suspend.html', profile=self.profile, title='Suspend User Profiles')

    def post(self, profile_id):
        """Pass the selected profile ID to the diagram onSuspend event."""
        self.onSuspend(profile_id)
        return self.rendered_page

    def onSuspend(self, profileId: int) -> None:
        """Check the ID and ask the controller to suspend the profile.

        Uses boundary/validation.py, control/profile/suspend_user_profile_controller.py, control/profile/view_user_profile_controller.py.
        """
        profileId = positive_integer(strip_input(profileId), 'Profile ID')
        controller = SuspendUserProfileController()
        if controller.suspendUserProfile(profileId):
            self.displaySuccess()
        else:
            self.profile = ViewUserProfileController().getUserProfile(profileId)
            self.error_message = controller.entity.error_message
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        """Show the suspension message and return to the profile list."""
        flash('User profile suspended successfully.', 'success')
        self.rendered_page = redirect(url_for('user_profiles'))

    def displayError(self) -> None:
        """Display a missing-profile or assigned-profile error."""
        if self.error_reason == 'not_found':
            self.rendered_page = render_template(
                'error.html', code=404, message=self.error_message,
                title='User Profile Not Found'), 404
        else:
            flash(self.error_message, 'error')
            self.rendered_page = render_template(
                'profiles/suspend.html', profile=self.profile, title='Suspend User Profiles'), 400
