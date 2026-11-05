from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import validate_profile_fields
from control.profile.create_user_profile_controller import CreateUserProfileController
from infrastructure.permissions import PERMISSION_OPTIONS


class CreateUserProfilePage(MethodView):

    def get(self):
        return render_template('profiles/create.html', values={}, errors={},
                               selected_permissions=[], permission_options=PERMISSION_OPTIONS)

    def post(self):
        status = {'Active': True, 'Suspended': False}.get(request.form.get('status', ''))
        self.onCreate(request.form.get('profileName', ''),
                      request.form.get('description', ''), status,
                      request.form.getlist('permissions'))
        return self.rendered_page

    def onCreate(self, profileName: str, description: str, status: bool,
                 permissions: list[str]) -> None:
        values, self.field_errors = validate_profile_fields(profileName, description, status, permissions)
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            self.displayError()
            return
        profileName, description, status, permissions = values
        controller = CreateUserProfileController()
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
        """Display input or duplicate errors alongside the submitted values."""
        flash(self.error_message, 'error')
        self.rendered_page = render_template(
            'profiles/create.html', values=request.form, errors=self.field_errors,
            selected_permissions=request.form.getlist('permissions'),
            permission_options=PERMISSION_OPTIONS), 400
