from control.profile.view_user_profile_controller import ViewUserProfileController
from flask import render_template, redirect, url_for, flash
from flask.views import MethodView
from control.profile.suspend_user_profile_controller import SuspendUserProfileController


class SuspendUserProfilePage(MethodView):

    def get(self, profile_id):
        self.profile = (ViewUserProfileController().getUserProfile(profile_id))
        if self.profile is None:
            self.error_message, self.error_reason = 'User profile not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template('profiles/suspend.html', profile=self.profile, title='Suspend User Profiles')

    def post(self, profile_id):
        self.onSuspend(profile_id)
        return self.rendered_page

    def onSuspend(self, profileId: int) -> None:
        controller = SuspendUserProfileController()
        self.profile = ViewUserProfileController().getUserProfile(profileId)
        if controller.suspendUserProfile(profileId):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        flash('User profile suspended successfully.', 'success')
        self.rendered_page = redirect(url_for('user_profiles'))

    def displayError(self) -> None:
        if self.error_reason == 'not_found':
            self.rendered_page = render_template(
                'error.html', code=404, message=self.error_message,
                title='User Profile Not Found'), 404
        else:
            flash(self.error_message, 'error')
            self.rendered_page = render_template(
                'profiles/suspend.html', profile=self.profile, title='Suspend User Profiles'), 400
