from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import validate_account_details, valid_account_id
from control.accounts.update_user_account_controller import UpdateUserAccountController


class UpdateUserAccountPage(MethodView):

    def get(self, account_id):
        controller = UpdateUserAccountController()
        account = controller.getUserAccount(account_id) if valid_account_id(account_id) else None
        if account is None:
            self.error_message, self.error_reason = 'User account not found.', 'not_found'
            self.displayError()
            return self.rendered_page
        return render_template('accounts/form.html', account=account,
            values={'full_name': account.full_name, 'email': account.email, 'profile_id': account.profile_id},
            errors={}, profiles=controller.activeProfiles(), editing=True, title='Update User Accounts')

    def post(self, account_id):
        self.onUpdate(account_id, request.form.get('full_name', ''),
                      request.form.get('email', ''), request.form.get('profile_id', type=int))
        return self.rendered_page

    def onUpdate(self, accountId: str, fullName: str, email: str, profileId: int) -> None:
        if not valid_account_id(accountId):
            self.error_message, self.error_reason = 'User account not found.', 'not_found'
            self.displayError()
            return
        values, self.field_errors = validate_account_details(fullName, email, profileId)
        if self.field_errors:
            self.error_message, self.error_reason = 'Please correct the errors below.', 'invalid_data'
            self.account = UpdateUserAccountController().getUserAccount(accountId)
            if self.account is None:
                self.error_message, self.error_reason = 'User account not found.', 'not_found'
            self.displayError()
            return
        fullName, email = values['full_name'], values['email']
        controller = UpdateUserAccountController()
        if controller.updateUserAccount(accountId, fullName, email, profileId):
            self.displaySuccess()
        else:
            self.error_message = controller.error_message
            self.field_errors = controller.field_errors
            self.error_reason = controller.error_reason
            self.account = controller.getUserAccount(accountId)
            if self.account is None:
                self.error_message, self.error_reason = 'User account not found.', 'not_found'
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
                profiles=UpdateUserAccountController().activeProfiles(),
                editing=True, title='Update User Accounts'), 400
