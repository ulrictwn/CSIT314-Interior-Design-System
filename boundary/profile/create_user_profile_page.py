from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import strip_input, validate_profile_fields
from control.profile.create_user_profile_controller import CreateUserProfileController
from infrastructure.permissions import PERMISSION_OPTIONS


class CreateUserProfilePage(MethodView):

    def get(self):
        return render_template('profiles/create.html', values={}, errors={},
                               selected_permissions=[], permission_options=PERMISSION_OPTIONS)

    def post(self):
        self.onCreate(request.form.get('profileName', ''),
                      request.form.get('description', ''),
                      request.form.get('status', ''),
                      request.form.getlist('permissions'))
        return self.rendered_page

    def onCreate(self, profileName: str, description: str, status: str,
                 permissions: list[str]) -> None:
        """Check input with boundary/validation.py before calling the profile controller."""
        values, errors = validate_profile_fields(
            strip_input(profileName), strip_input(description), strip_input(status), permissions)
        if errors:
            self.error_message, self.field_errors = 'Please correct the errors below.', errors
            self.displayError()
            return
        controller = CreateUserProfileController()
        if controller.createUserProfile(*values):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.field_errors = controller.entity.field_errors
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
