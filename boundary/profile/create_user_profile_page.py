from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
# Input cleanup and field checks from boundary/validation.py.
from boundary.validation import strip_input, validate_profile_fields
# Controller used to relay this boundary request from control/profile/create_user_profile_controller.py.
from control.profile.create_user_profile_controller import CreateUserProfileController
# Permission labels displayed in the form from infrastructure/permissions.py.
from infrastructure.permissions import PERMISSION_OPTIONS


class CreateUserProfilePage(MethodView):

    def get(self):
        """Display an empty profile creation form."""
        return render_template('profiles/create.html', values={}, errors={},
                               selected_permissions=[], permission_options=PERMISSION_OPTIONS)

    def post(self):
        """Read submitted fields and call the diagram onCreate event."""
        status = request.form.get('status', '')
        self.onCreate(request.form.get('profileName', ''),
                      request.form.get('description', ''), status,
                      request.form.getlist('permissions'))
        return self.rendered_page

    def onCreate(self, profileName: str, description: str, status: str,
                 permissions: list[str]) -> None:
        """Validate the profile input, then ask the controller to create it.

        Uses boundary/validation.py, control/profile/create_user_profile_controller.py.
        """
        values, errors = validate_profile_fields(strip_input(profileName), strip_input(description),
                                                 strip_input(status), permissions)
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
        """Show the creation message and return to the profile list."""
        flash('User profile created successfully.', 'success')
        self.rendered_page = redirect(url_for('user_profiles'))

    def displayError(self) -> None:
        """Display the submitted values and their field or duplicate errors."""
        flash(self.error_message, 'error')
        self.rendered_page = render_template(
            'profiles/create.html', values=request.form, errors=self.field_errors,
            selected_permissions=request.form.getlist('permissions'),
            permission_options=PERMISSION_OPTIONS), 400
