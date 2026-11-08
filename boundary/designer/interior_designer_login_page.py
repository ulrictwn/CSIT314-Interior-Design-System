from flask import redirect, render_template, session, url_for
from flask.views import MethodView
from boundary.designer.presentation import wants_html
from boundary.validation import strip_input
from boundary.designer.context import request_values
from boundary.designer.responses import error_response
from control.designer.interior_designer_login_controller import InteriorDesignerLoginController


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
        self.username = strip_input(username)
        controller = InteriorDesignerLoginController()
        if controller.login(self.username, password):
            session.clear()
            session['account_id'] = controller.entity.authenticated_account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.displayError()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(url_for('designer_dashboard'))

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            values={'username': self.username})
