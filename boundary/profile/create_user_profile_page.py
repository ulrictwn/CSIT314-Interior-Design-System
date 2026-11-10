from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import strip_input
from control.profile.create_user_profile_controller import CreateUserProfileController
from infrastructure.permissions import PERMISSION_OPTIONS


class CreateUserProfilePage(MethodView):

    def get(self):
        """Display the empty profile form and permission labels."""
        return render_template('profiles/create.html', values={}, errors={},
                               selected_permissions=[], permission_options=PERMISSION_OPTIONS)

    def post(self):
        """Read submitted fields and pass them to the onCreate event."""
        self.onCreate(request.form.get('profileName', ''),
                      request.form.get('description', ''),
                      request.form.get('status', ''),
                      request.form.getlist('permissions'))
        return self.rendered_page

    def onCreate(self, profileName: str, description: str, status: str,
                 permissions: list[str]) -> None:
        """Strip fields and display the entity result from CreateUserProfileController.

        Uses boundary/validation.py and control/profile/create_user_profile_controller.py.
        """
        controller = CreateUserProfileController()
        if controller.createUserProfile(strip_input(profileName), strip_input(description),
                                        strip_input(status), permissions):
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
        """Display input or duplicate errors alongside the submitted values."""
        flash(self.error_message, 'error')
        self.rendered_page = render_template(
            'profiles/create.html', values=request.form, errors=self.field_errors,
            selected_permissions=request.form.getlist('permissions'),
            permission_options=PERMISSION_OPTIONS), 400
