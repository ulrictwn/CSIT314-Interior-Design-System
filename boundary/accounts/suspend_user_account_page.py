# Controller used to relay this boundary request from control/accounts/view_user_account_controller.py.
from control.accounts.view_user_account_controller import ViewUserAccountController
from flask import render_template, redirect, url_for, flash
from flask.views import MethodView
# Input cleanup and field checks from boundary/validation.py.
from boundary.validation import strip_input, valid_account_id
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError
# Controller used to relay this boundary request from control/accounts/suspend_user_account_controller.py.
from control.accounts.suspend_user_account_controller import SuspendUserAccountController


class SuspendUserAccountPage(MethodView):

    def get(self, account_id):
        """Load the selected account for suspension confirmation.

        Uses boundary/validation.py, control/accounts/view_user_account_controller.py.
        """
        account_id = strip_input(account_id)
        if not valid_account_id(account_id):
            raise DomainError('Enter a valid account ID.')
        self.account = ViewUserAccountController().getUserAccount(account_id)
        if self.account is None:
            return render_template('error.html', code=404, message='User account not found.',
                                   title='User Account Not Found'), 404
        return render_template('accounts/suspend.html', account=self.account, title='Suspend User Accounts')

    def post(self, account_id):
        """Pass the selected account ID to the diagram onSuspend event."""
        self.onSuspend(account_id)
        return self.rendered_page

    def onSuspend(self, accountId: str) -> None:
        """Check the ID, request suspension and display any saved-state error.

        Uses boundary/validation.py, control/accounts/suspend_user_account_controller.py, control/accounts/view_user_account_controller.py.
        """
        accountId = strip_input(accountId)
        if not valid_account_id(accountId):
            raise DomainError('Enter a valid account ID.')
        controller = SuspendUserAccountController()
        if controller.suspendUserAccount(accountId):
            self.displaySuccess()
        else:
            self.account = ViewUserAccountController().getUserAccount(accountId)
            self.error_message = controller.entity.error_message
            self.error_reason = controller.entity.error_reason
            if self.error_reason == 'not_found':
                self.rendered_page = render_template('error.html', code=404, message=self.error_message,
                                                    title='User Account Not Found'), 404
            else:
                flash(self.error_message, 'error')
                self.rendered_page = render_template('accounts/suspend.html', account=self.account,
                                                    title='Suspend User Accounts'), 400

    def displaySuccess(self) -> None:
        """Show the suspension message and return to the account list."""
        flash('User account suspended successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))
