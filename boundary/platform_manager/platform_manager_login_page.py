from flask import redirect, render_template, session, url_for
from flask.views import MethodView
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, validate_login_credentials
# boundary/designer/context.py: submitted values and signed-in account context.
from boundary.designer.context import request_values
# boundary/designer/presentation.py: HTML or JSON presentation choice.
from boundary.designer.presentation import wants_html
# control/platform_manager/platform_manager_login_controller.py: the boundary-to-entity request handler.
from control.platform_manager.platform_manager_login_controller import PlatformManagerLoginController


class PlatformManagerLoginPage(MethodView):
    def get(self):
        """Display the manager login form or its JSON field information."""
        if wants_html():
            return render_template('auth/login.html', login_role='manager', values={}, errors={}, title='Platform Manager Sign In')
        return dict(ok=True, fields=['username','password'], values={'username':''})

    def post(self):
        """Read the submitted request, run onLogin, and return the prepared response."""
        values = request_values()
        self.onLogin(values.get('username',''), values.get('password',''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
        """Check credential fields, then request login through the role-specific controller."""
        self.username = strip_input(username)
        try:
            self.username = validate_login_credentials(self.username, password)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), error.field_errors
            self.displayError()
            return
        controller = PlatformManagerLoginController()
        if controller.login(self.username, password):
            session.clear()
            session['account_id'] = controller.entity.authenticated_account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.displayError()

    def displayDashboard(self) -> None:
        """Prepare the redirect to the signed-in user's dashboard."""
        self.rendered_page = redirect(url_for('platform_manager_dashboard'))

    def displayError(self) -> None:
        """Display the input or saved-data error returned by this operation."""
        values = {'username':self.username}
        if wants_html():
            self.rendered_page = render_template('auth/login.html',login_role='manager', values=values,
                errors=self.field_errors, error_message=self.error_message, title='Platform Manager Sign In'), 400
        else:
            self.rendered_page = dict(ok=False, message=self.error_message, errors=self.field_errors, values=values), 400
