from control.accounts.view_user_account_controller import ViewUserAccountController
from flask import render_template, redirect, url_for, flash
from flask.views import MethodView
from control.accounts.suspend_user_account_controller import SuspendUserAccountController


class SuspendUserAccountPage(MethodView):

    def get(self, account_id):
        self.account = (ViewUserAccountController().getUserAccount(account_id))
        if self.account is None:
            self.error_message, self.error_reason = 'User account not found.', 'not_found'
            self._display_error()
            return self.rendered_page
        return render_template('accounts/suspend.html', account=self.account, title='Suspend User Accounts')

    def post(self, account_id):
        self.onSuspend(account_id)
        return self.rendered_page

    def onSuspend(self, accountId: str) -> None:
        controller = SuspendUserAccountController()
        self.account = ViewUserAccountController().getUserAccount(accountId)
        if controller.suspendUserAccount(accountId):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.error_reason = controller.entity.error_reason
            self._display_error()

    def displaySuccess(self) -> None:
        flash('User account suspended successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))

    def _display_error(self) -> None:
        if self.error_reason == 'not_found':
            self.rendered_page = render_template(
                'error.html', code=404, message=self.error_message,
                title='User Account Not Found'), 404
        else:
            flash(self.error_message, 'error')
            self.rendered_page = render_template(
                'accounts/suspend.html', account=self.account, title='Suspend User Accounts'), 400
