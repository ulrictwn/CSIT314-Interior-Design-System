from flask import g, session, redirect, url_for, request, render_template
from flask.views import MethodView
# boundary/validation.py: strips ordinary submitted text only.
from boundary.validation import strip_input
# control/auth/user_admin_login_controller.py: provides the controller used to communicate with its entity.
from control.auth.user_admin_login_controller import UserAdminLoginController
# infrastructure/navigation.py: builds sidebar links and selects role dashboards.
from infrastructure.navigation import dashboard_endpoint


class UserAdminLoginPage(MethodView):
    def get(self):
        """Display the login form or open the signed-in account's dashboard."""
        if g.current_user:
            return redirect(url_for(dashboard_endpoint(g.current_user)))
        return render_template('auth/login.html', values={}, errors={}, login_role='admin', title='User Admin Login')

    def post(self):
        """Read the submitted credentials and pass them to onLogin()."""
        self.onLogin(request.form.get('username', ''), request.form.get('password', ''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
        """Strip the username and call UserAdminLoginController from control/auth/user_admin_login_controller.py."""
        self.username = strip_input(username)
        controller = UserAdminLoginController()
        if controller.login(self.username, password):
            session.clear()
            session['account_id'] = controller.entity.authenticated_account.account_id
            self.displayDashboard()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.displayError()

    def displayDashboard(self) -> None:
        """Redirect a successful admin login to the dashboard."""
        self.rendered_page = redirect(url_for('dashboard'))

    def displayError(self) -> None:
        """Redisplay the username and validation or credential errors."""
        self.rendered_page = (render_template('auth/login.html',
            values={'username': request.form.get('username', '')}, errors=self.field_errors,
            title='User Admin Login', login_role='admin', error_message=self.error_message), 400)
