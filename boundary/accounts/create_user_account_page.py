from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import validate_account_fields
from control.accounts.create_user_account_controller import CreateUserAccountController


class CreateUserAccountPage(MethodView):

    def get(self):
        return render_template('accounts/form.html', values={}, errors={}, account=None,
            profiles=CreateUserAccountController().activeProfiles(),
            editing=False, title='Create User Accounts')

    def post(self):
        self.clickCreate(request.form.get('username', ''), request.form.get('full_name', ''),
                         request.form.get('email', ''), request.form.get('phone_number', ''),
                         request.form.get('profile_id', type=int))
        return self.rendered_page

    def clickCreate(self, username: str, fullName: str, email: str,
                    phoneNumber: str, profileId: int) -> None:
        values, self.field_errors = validate_account_fields(username, fullName, email, phoneNumber, profileId)
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            self.displayError()
            return
        username, fullName = values['username'], values['full_name']
        email, phoneNumber = values['email'], values['phone_number']
        controller = CreateUserAccountController()
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
            profiles=CreateUserAccountController().activeProfiles(),
            editing=False, title='Create User Accounts'), 400
