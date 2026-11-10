# Controller used to relay this boundary request from control/profile/search_user_profile_controller.py.
from control.profile.search_user_profile_controller import SearchUserProfileController
# Controller used to relay this boundary request from control/accounts/view_user_account_controller.py.
from control.accounts.view_user_account_controller import ViewUserAccountController
from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
# Input cleanup and field checks from boundary/validation.py.
from boundary.validation import strip_input, validate_account_details, valid_account_id
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError
# Controller used to relay this boundary request from control/accounts/update_user_account_controller.py.
from control.accounts.update_user_account_controller import UpdateUserAccountController


class UpdateUserAccountPage(MethodView):

    def get(self, account_id):
        """Load the saved account and active profiles for the update form.

        Uses boundary/validation.py, control/accounts/view_user_account_controller.py, control/profile/search_user_profile_controller.py.
        """
        account_id = strip_input(account_id)
        if not valid_account_id(account_id):
            raise DomainError('Enter a valid account ID.')
        account = ViewUserAccountController().getUserAccount(account_id)
        if account is None:
            self.error_message, self.error_reason = 'User account not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template('accounts/form.html', account=account,
            values={'full_name': account.full_name, 'email': account.email, 'profile_id': account.profile_id},
            errors={}, profiles=[profile for profile in SearchUserProfileController().searchUserProfiles('')
                      if profile.status == 'Active'], editing=True, title='Update User Accounts')

    def post(self, account_id):
        """Read edited account fields and call the diagram onUpdate event."""
        self.onUpdate(account_id, request.form.get('full_name', ''),
                      request.form.get('email', ''), request.form.get('profile_id', ''))
        return self.rendered_page

    def onUpdate(self, accountId: str, fullName: str, email: str, profileId: int) -> None:
        """Validate the edited fields, then ask the controller to update the account.

        Uses boundary/validation.py, control/accounts/update_user_account_controller.py, control/accounts/view_user_account_controller.py.
        """
        accountId = strip_input(accountId)
        if not valid_account_id(accountId):
            raise DomainError('Enter a valid account ID.')
        values, errors = validate_account_details(strip_input(fullName), strip_input(email), strip_input(profileId))
        if errors:
            self.error_message, self.field_errors = 'Please correct the errors below.', errors
            self.error_reason = 'invalid_data'
            self.account = ViewUserAccountController().getUserAccount(accountId)
            self.displayError()
            return
        controller = UpdateUserAccountController()
        if controller.updateUserAccount(accountId, values['full_name'], values['email'], values['profile_id']):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.field_errors = controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.account = ViewUserAccountController().getUserAccount(accountId)
            self.displayError()

    def displaySuccess(self) -> None:
        """Show the update message and return to the account list."""
        flash('User account updated successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))

    def displayError(self) -> None:
        """Display a missing-account error or the invalid update form.

        Uses control/profile/search_user_profile_controller.py.
        """
        if self.error_reason == 'not_found':
            self.rendered_page = render_template(
                'error.html', code=404, message=self.error_message,
                title='User Account Not Found'), 404
        else:
            flash(self.error_message, 'error')
            self.rendered_page = render_template('accounts/form.html', account=self.account,
                values=request.form, errors=self.field_errors,
                profiles=[profile for profile in SearchUserProfileController().searchUserProfiles('')
                      if profile.status == 'Active'],
                editing=True, title='Update User Accounts'), 400
