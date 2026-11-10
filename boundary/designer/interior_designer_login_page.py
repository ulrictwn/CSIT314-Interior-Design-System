from flask import redirect, render_template, session, url_for
from flask.views import MethodView
# infrastructure/errors.py: defines expected validation, missing-record and access errors.
from infrastructure.errors import DomainError
# boundary/designer/presentation.py: chooses designer HTML/JSON responses.
from boundary.designer.presentation import wants_html
# boundary/validation.py: trims and checks submitted input fields.
from boundary.validation import strip_input, validate_login_credentials
# boundary/designer/context.py: reads form/JSON values and the signed-in account.
from boundary.designer.context import request_values
# boundary/designer/responses.py: formats designer validation/entity errors.
from boundary.designer.responses import error_response
# control/designer/interior_designer_login_controller.py: provides the controller used to communicate with its entity.
from control.designer.interior_designer_login_controller import InteriorDesignerLoginController


class InteriorDesignerLoginPage(MethodView):
    def get(self):
        """Display the designer login form or return its input fields as JSON."""
        if wants_html():
            return render_template('auth/login.html', login_role='designer', values={}, errors={}, title='Interior Designer Sign In')
        return dict(ok=True, fields=['username', 'password'], values={'username': ''})

    def post(self):
        """Read the submitted credentials and pass them to onLogin()."""
        values = request_values()
        self.onLogin(values.get('username', ''), values.get('password', ''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
        """Check fields, then call InteriorDesignerLoginController from control/designer/interior_designer_login_controller.py."""
        self.username = strip_input(username)
        try:
            self.username = validate_login_credentials(self.username, password)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), error.field_errors
            self.displayError()
            return
        controller = InteriorDesignerLoginController()
        if controller.login(self.username, password):
            session.clear()
            session['account_id'] = controller.entity.authenticated_account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.displayError()

    def displayDashboard(self) -> None:
        """Redirect a successful designer login to the designer dashboard."""
        self.rendered_page = redirect(url_for('designer_dashboard'))

    def displayError(self) -> None:
        """Display credential or field errors through boundary/designer/responses.py."""
        self.rendered_page = error_response(self.error_message, self.field_errors,
            values={'username': self.username})
