from flask import render_template, request, redirect, url_for, flash
from flask.views import MethodView
from boundary.validation import strip_input
from control.accounts.create_user_account_controller import CreateUserAccountController


class CreateUserAccountPage(MethodView):

    def get(self):
        return render_template('accounts/form.html', values={}, errors={}, account=None,
            profiles=CreateUserAccountController().activeProfiles(),
            editing=False, title='Create User Accounts')

    def post(self):
        self.onCreate(request.form.get('username', ''), request.form.get('full_name', ''),
                         request.form.get('email', ''), request.form.get('phone_number', ''),
                         request.form.get('profile_id', ''))
        return self.rendered_page

    def onCreate(self, username: str, fullName: str, email: str,
                    phoneNumber: str, profileId: int) -> None:
        controller = CreateUserAccountController()
        if controller.createUserAccount(strip_input(username), strip_input(fullName), strip_input(email), strip_input(phoneNumber), strip_input(profileId)):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.field_errors = controller.entity.field_errors
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
