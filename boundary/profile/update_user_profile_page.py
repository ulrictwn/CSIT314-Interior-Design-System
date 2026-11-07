from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import validate_profile_fields, valid_profile_id
from control.profile.update_user_profile_controller import UpdateUserProfileController
from infrastructure.permissions import PERMISSION_OPTIONS


class UpdateUserProfilePage(MethodView):

    def get(self, profile_id):
        profile = (UpdateUserProfileController().getUserProfile(profile_id)
                   if valid_profile_id(profile_id) else None)
        if profile is None:
            self.error_message, self.error_reason = 'User profile not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template(
            'profiles/form.html', values={'profileName': profile.name,
                'description': profile.description, 'status': profile.status}, errors={},
            selected_permissions=profile.permissions, permission_options=PERMISSION_OPTIONS)

    def post(self, profile_id):
        self.onUpdate(profile_id, request.form.get('profileName', ''),
                      request.form.get('description', ''), request.form.getlist('permissions'))
        return self.rendered_page

    def onUpdate(self, profileId: int, profileName: str, description: str,
                 permissions: list[str]) -> None:
        if not valid_profile_id(profileId):
            self.error_message, self.error_reason = 'User profile not found.', 'not_found'
            self.displayError()
            return
        values, self.field_errors = validate_profile_fields(
            profileName, description, 'Active', permissions)
        if self.field_errors:
            self.error_message, self.error_reason = 'Please correct the errors below.', 'invalid_data'
            self.displayError()
            return
        profileName, description, _, permissions = values
        controller = UpdateUserProfileController()
        if controller.updateUserProfile(profileId, profileName, description, permissions):
            self.displaySuccess()
        else:
            self.error_message = controller.error_message
            self.field_errors = controller.field_errors
            self.error_reason = controller.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        flash('User profile updated successfully.', 'success')
        self.rendered_page = redirect(url_for('user_profiles'))

    def displayError(self) -> None:
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
