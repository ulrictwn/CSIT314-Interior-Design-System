from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
# Input cleanup and field checks from boundary/validation.py.
from boundary.validation import strip_input, validate_profile_fields, positive_integer
# Controller used to relay this boundary request from control/profile/update_user_profile_controller.py.
from control.profile.update_user_profile_controller import UpdateUserProfileController
# Permission labels displayed in the form from infrastructure/permissions.py.
from infrastructure.permissions import PERMISSION_OPTIONS


class UpdateUserProfilePage(MethodView):

    def get(self, profile_id):
        """Load the saved profile and prefill the update form.

        Uses boundary/validation.py, control/profile/update_user_profile_controller.py.
        """
        profile = UpdateUserProfileController().getUserProfile(positive_integer(profile_id, 'Profile ID'))
        if profile is None:
            self.error_message, self.error_reason = 'User profile not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template(
            'profiles/form.html', values={'profileName': profile.name,
                'description': profile.description, 'status': profile.status}, errors={},
            selected_permissions=profile.permissions, permission_options=PERMISSION_OPTIONS)

    def post(self, profile_id):
        """Read edited fields and call the diagram onUpdate event."""
        self.onUpdate(profile_id, request.form.get('profileName', ''),
                      request.form.get('description', ''), request.form.getlist('permissions'))
        return self.rendered_page

    def onUpdate(self, profileId: int, profileName: str, description: str,
                 permissions: list[str]) -> None:
        """Validate the edited fields, then ask the controller to update the profile.

        Uses boundary/validation.py, control/profile/update_user_profile_controller.py.
        """
        profileId = positive_integer(strip_input(profileId), 'Profile ID')
        values, errors = validate_profile_fields(strip_input(profileName), strip_input(description),
                                                 'Active', permissions)
        if errors:
            self.error_message, self.field_errors = 'Please correct the errors below.', errors
            self.error_reason = 'invalid_data'
            self.displayError()
            return
        profileName, description, _, permissions = values
        controller = UpdateUserProfileController()
        if controller.updateUserProfile(profileId, profileName, description, permissions):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.field_errors = controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        """Show the update message and return to the profile list."""
        flash('User profile updated successfully.', 'success')
        self.rendered_page = redirect(url_for('user_profiles'))

    def displayError(self) -> None:
        """Display a missing-profile error or the invalid update form."""
        if self.error_reason == 'not_found':
            self.rendered_page = render_template(
                'error.html', code=404, message=self.error_message,
                title='User Profile Not Found'), 404
        else:
            flash(self.error_message, 'error')
            self.rendered_page = render_template(
                'profiles/form.html', values=request.form, errors=self.field_errors,
                selected_permissions=request.form.getlist('permissions'),
                permission_options=PERMISSION_OPTIONS), 400
