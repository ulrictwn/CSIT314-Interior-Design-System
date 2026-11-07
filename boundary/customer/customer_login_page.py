from flask import redirect, render_template, session, url_for
from flask.views import MethodView
from boundary.validation import validate_login_credentials
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from control.customer.customer_login_controller import CustomerLoginController
from infrastructure.errors import DomainError


class CustomerLoginPage(MethodView):
    def get(self):
        if wants_html():
            return render_template('auth/login.html', login_role='customer', values={}, errors={}, title='Customer Sign In')
        return dict(ok=True, fields=['username','password'], values={'username':''})

    def post(self):
        values = request_values()
        self.onLogin(values.get('username',''), values.get('password',''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
        self.username = username
        try:
            username = validate_login_credentials(username, password)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), error.field_errors
            self.displayError()
            return
        controller = CustomerLoginController()
        if controller.login(username,password):
            session.clear()
            session['account_id'] = controller.account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.error_message, {}
            self.displayError()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(url_for('customer_dashboard'))

    def displayError(self) -> None:
        values = {'username':self.username}
        if wants_html():
            self.rendered_page = render_template('auth/login.html',login_role='customer', values=values,
                errors=self.field_errors, error_message=self.error_message, title='Customer Sign In'), 400
        else:
            self.rendered_page = dict(ok=False, message=self.error_message, errors=self.field_errors, values=values), 400
