# Controller used to relay this boundary request from control/accounts/view_user_account_controller.py.
from control.accounts.view_user_account_controller import ViewUserAccountController
from flask import render_template, redirect, url_for, flash
from flask.views import MethodView
# Ordinary input cleanup from boundary/validation.py; entities validate the values.
from boundary.validation import strip_input
# Controller used to relay this boundary request from control/accounts/suspend_user_account_controller.py.
from control.accounts.suspend_user_account_controller import SuspendUserAccountController


class SuspendUserAccountPage(MethodView):

    def get(self, account_id):
        """Load the selected account for suspension confirmation.

        Uses boundary/validation.py, control/accounts/view_user_account_controller.py.
        """
        account_id = strip_input(account_id)
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
        """Strip the ID, request suspension and display the entity's result.

        Uses boundary/validation.py, control/accounts/suspend_user_account_controller.py, control/accounts/view_user_account_controller.py.
        """
        accountId = strip_input(accountId)
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
