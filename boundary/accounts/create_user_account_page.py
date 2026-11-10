# Controller used to relay profile choices from control/profile/view_user_profile_controller.py.
from control.profile.view_user_profile_controller import ViewUserProfileController
from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
# Ordinary input cleanup from boundary/validation.py; entities validate the values.
from boundary.validation import strip_input
# Controller used to relay this boundary request from control/accounts/create_user_account_controller.py.
from control.accounts.create_user_account_controller import CreateUserAccountController


class CreateUserAccountPage(MethodView):

    def get(self):
        """Display an empty account form and active profile choices.

        Uses control/profile/view_user_profile_controller.py.
        """
        return render_template('accounts/form.html', values={}, errors={}, account=None,
            profiles=[profile for profile in ViewUserProfileController().listUserProfiles()
                      if profile.status == 'Active'],
            editing=False, title='Create User Accounts')

    def post(self):
        """Read the account form and supply the default password to onCreate."""
        self.onCreate(request.form.get('username', ''), 'password', request.form.get('full_name', ''),
                         request.form.get('email', ''), request.form.get('phone_number', ''),
                         request.form.get('profile_id', ''))
        return self.rendered_page

    def onCreate(self, username: str, password: str, fullName: str, email: str,
                    phoneNumber: str, profileId: int) -> None:
        """Strip account fields and pass them to the validating account entity through its controller.

        Uses boundary/validation.py, control/accounts/create_user_account_controller.py.
        """
        controller = CreateUserAccountController()
        if controller.createUserAccount(strip_input(username), password, strip_input(fullName),
                                        strip_input(email), strip_input(phoneNumber), strip_input(profileId)):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.field_errors = controller.entity.field_errors
            self.displayError()

    def displaySuccess(self) -> None:
        """Show the creation message and return to the account list."""
        flash('User account created successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))

    def displayError(self) -> None:
        """Redisplay the account fields and their input or duplicate errors.

        Uses control/profile/view_user_profile_controller.py.
        """
        flash(self.error_message, 'error')
        self.rendered_page = render_template(
            'accounts/form.html', values=request.form, errors=self.field_errors, account=None,
            profiles=[profile for profile in ViewUserProfileController().listUserProfiles()
                      if profile.status == 'Active'],
            editing=False, title='Create User Accounts'), 400
