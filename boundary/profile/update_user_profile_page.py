from flask import render_template, request, redirect, url_for, flash
from boundary.base import Page
from control.profile.update_user_profile_controller import UpdateUserProfileController
from infrastructure.permissions import PERMISSION_OPTIONS


class UpdateUserProfilePage(Page):
    permission = 'profile.update'

    def get(self, profile_id):
        profile = UpdateUserProfileController(self.actor).getUserProfile(profile_id)
        if profile is None:
            self.error_message, self.error_reason = 'User profile not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template(
            'profiles/form.html', values={'profileName': profile.name,
                'description': profile.description, 'status': profile.status}, errors={},
            selected_permissions=profile.permissions, permission_options=PERMISSION_OPTIONS)

    def post(self, profile_id):
        selected_status = request.form.get('status', '')
        status = {'Active': True, 'Suspended': False}.get(selected_status, selected_status)
        self.onUpdate(profile_id, request.form.get('profileName', ''),
                      request.form.get('description', ''), request.form.getlist('permissions'), status)
        return self.rendered_page

    def onUpdate(self, profileId: int, profileName: str, description: str,
                 permissions: list[str], status: bool | None = None) -> None:
        controller = UpdateUserProfileController(self.actor)
        if controller.updateUserProfile(profileId, profileName, description, permissions, status):
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
