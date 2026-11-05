from flask import g, session, redirect, url_for, request, render_template
from flask.views import MethodView
from boundary.validation import validate_login_credentials
from control.auth.login_controller import LoginController
from infrastructure.errors import DomainError


class LoginPage(MethodView):
    def get(self):
        if g.current_user:
            return redirect(url_for('designer_dashboard' if g.current_user.profile.name.casefold() == 'interior designer' else 'dashboard'))
        return render_template('auth/login.html', values={}, errors={}, login_role='admin', title='User Admin Login')

    def post(self):
        self.clickLogin(request.form.get('username', ''), request.form.get('password', ''))
        return self.rendered_page

    def clickLogin(self, username: str, password: str) -> None:
        try:
            username = validate_login_credentials(username, password)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), error.field_errors
            self.displayError()
            return
        controller = LoginController()
        if controller.login(username, password):
            session.clear()
            session['account_id'] = controller.account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.error_message, {}
            self.displayError()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(url_for('dashboard'))

    def displayError(self) -> None:
        self.rendered_page = (render_template('auth/login.html',
            values={'username': request.form.get('username', '')}, errors=self.field_errors,
            title='User Admin Login', login_role='admin', error_message=self.error_message), 400)
