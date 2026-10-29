from flask import render_template, request, redirect, url_for, flash
from boundary.base import Page
from control.profile.create_user_profile_controller import CreateUserProfileController
from infrastructure.permissions import PERMISSION_OPTIONS


class CreateUserProfilePage(Page):
    permission = 'profile.create'

    def get(self):
        return render_template('profiles/create.html', values={}, errors={},
                               selected_permissions=[], permission_options=PERMISSION_OPTIONS)

    def post(self):
        status = {'Active': True, 'Suspended': False}.get(request.form.get('status', ''))
        self.clickCreate(request.form.get('profileName', ''),
                         request.form.get('description', ''), status,
                         request.form.getlist('permissions'))
        return self.rendered_page

    def clickCreate(self, profileName: str, description: str, status: bool,
                    permissions: list[str]) -> None:
        controller = CreateUserProfileController(self.actor)
        if controller.createUserProfile(profileName, description, status, permissions):
            self.displaySuccess()
        else:
            self.error_message = controller.error_message
            self.field_errors = controller.field_errors
            self.displayError()

    def displaySuccess(self) -> None:
        flash('User profile created successfully.', 'success')
        self.rendered_page = redirect(url_for('user_profiles'))

    def displayError(self) -> None:
        """Display the entity's errors alongside the submitted values."""
        flash(self.error_message, 'error')
        self.rendered_page = render_template(
            'profiles/create.html', values=request.form, errors=self.field_errors,
            selected_permissions=request.form.getlist('permissions'),
            permission_options=PERMISSION_OPTIONS), 400
