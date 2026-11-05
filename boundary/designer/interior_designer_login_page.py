from flask import redirect, render_template, session, url_for
from flask.views import MethodView
from boundary.designer.presentation import wants_html
from boundary.validation import validate_login_credentials
from boundary.designer.context import request_values
from boundary.designer.responses import error_response
from control.designer.interior_designer_login_controller import InteriorDesignerLoginController
from infrastructure.errors import DomainError


class InteriorDesignerLoginPage(MethodView):
    def get(self):
        if wants_html():
            return render_template('auth/login.html', login_role='designer', values={}, errors={}, title='Interior Designer Sign In')
        return dict(ok=True, fields=['username', 'password'], values={'username': ''})

    def post(self):
        values = request_values()
        self.onLogin(values.get('username', ''), values.get('password', ''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
        self.username = username
        try:
            username = validate_login_credentials(username, password)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), error.field_errors
            self.displayError()
            return
        controller = InteriorDesignerLoginController()
        if controller.login(username, password):
            session.clear()
            session['account_id'] = controller.account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.error_message, {}
            self.displayError()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(url_for('designer_dashboard'))

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            values={'username': self.username})
