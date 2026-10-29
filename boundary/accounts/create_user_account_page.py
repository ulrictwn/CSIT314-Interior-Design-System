from flask import render_template, request, redirect, url_for, flash
from boundary.base import Page
from control.accounts.create_user_account_controller import CreateUserAccountController


class CreateUserAccountPage(Page):
    permission = 'account.create'

    def get(self):
        return render_template('accounts/form.html', values={}, errors={}, account=None,
            profiles=CreateUserAccountController(self.actor).activeProfiles(),
            editing=False, title='Create User Accounts')

    def post(self):
        self.clickCreate(request.form.get('username', ''), request.form.get('full_name', ''),
                         request.form.get('email', ''), request.form.get('phone_number', ''),
                         request.form.get('profile_id', type=int))
        return self.rendered_page

    def clickCreate(self, username: str, fullName: str, email: str,
                    phoneNumber: str, profileId: int) -> None:
        controller = CreateUserAccountController(self.actor)
        if controller.createUserAccount(username, fullName, email, phoneNumber, profileId):
            self.displaySuccess()
        else:
            self.error_message = controller.error_message
            self.field_errors = controller.field_errors
            self.displayError()

    def displaySuccess(self) -> None:
        flash('User account created successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))

    def displayError(self) -> None:
        flash(self.error_message, 'error')
        self.rendered_page = render_template(
            'accounts/form.html', values=request.form, errors=self.field_errors, account=None,
            profiles=CreateUserAccountController(self.actor).activeProfiles(),
            editing=False, title='Create User Accounts'), 400
