from control.profile.profile_controllers import ProfileDirectoryController
from control.accounts.view_user_account_controller import ViewUserAccountController
from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import strip_input
from control.accounts.update_user_account_controller import UpdateUserAccountController


class UpdateUserAccountPage(MethodView):

    def get(self, account_id):
        controller = UpdateUserAccountController()
        account = ViewUserAccountController().getUserAccount(account_id)
        if account is None:
            self.error_message, self.error_reason = 'User account not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template('accounts/form.html', account=account,
            values={'full_name': account.full_name, 'email': account.email, 'profile_id': account.profile_id},
            errors={}, profiles=ProfileDirectoryController().activeProfiles(), editing=True, title='Update User Accounts')

    def post(self, account_id):
        self.onUpdate(account_id, request.form.get('full_name', ''),
                      request.form.get('email', ''), request.form.get('profile_id', ''))
        return self.rendered_page

    def onUpdate(self, accountId: str, fullName: str, email: str, profileId: int) -> None:
        controller = UpdateUserAccountController()
        if controller.updateUserAccount(strip_input(accountId), strip_input(fullName), strip_input(email), strip_input(profileId)):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.field_errors = controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.account = ViewUserAccountController().getUserAccount(accountId)
            self.displayError()

    def displaySuccess(self) -> None:
        flash('User account updated successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))

    def displayError(self) -> None:
        if self.error_reason == 'not_found':
            self.rendered_page = render_template(
                'error.html', code=404, message=self.error_message,
                title='User Account Not Found'), 404
        else:
            flash(self.error_message, 'error')
            self.rendered_page = render_template('accounts/form.html', account=self.account,
                values=request.form, errors=self.field_errors,
                profiles=ProfileDirectoryController().activeProfiles(),
                editing=True, title='Update User Accounts'), 400
