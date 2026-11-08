from flask import redirect, render_template, session, url_for
from flask.views import MethodView
from boundary.validation import strip_input
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from control.platform_manager.platform_manager_login_controller import PlatformManagerLoginController


class PlatformManagerLoginPage(MethodView):
    def get(self):
        if wants_html():
            return render_template('auth/login.html', login_role='manager', values={}, errors={}, title='Platform Manager Sign In')
        return dict(ok=True, fields=['username','password'], values={'username':''})

    def post(self):
        values = request_values()
        self.onLogin(values.get('username',''), values.get('password',''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
        self.username = strip_input(username)
        controller = PlatformManagerLoginController()
        if controller.login(self.username, password):
            session.clear()
            session['account_id'] = controller.entity.authenticated_account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.displayError()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(url_for('platform_manager_dashboard'))

    def displayError(self) -> None:
        values = {'username':self.username}
        if wants_html():
            self.rendered_page = render_template('auth/login.html',login_role='manager', values=values,
                errors=self.field_errors, error_message=self.error_message, title='Platform Manager Sign In'), 400
        else:
            self.rendered_page = dict(ok=False, message=self.error_message, errors=self.field_errors, values=values), 400
