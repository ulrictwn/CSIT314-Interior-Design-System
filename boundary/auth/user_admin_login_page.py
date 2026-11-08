from flask import g, session, redirect, url_for, request, render_template
from flask.views import MethodView
from boundary.validation import strip_input
from control.auth.user_admin_login_controller import UserAdminLoginController
from infrastructure.navigation import dashboard_endpoint


class UserAdminLoginPage(MethodView):
    def get(self):
        if g.current_user:
            return redirect(url_for(dashboard_endpoint(g.current_user)))
        return render_template('auth/login.html', values={}, errors={}, login_role='admin', title='User Admin Login')

    def post(self):
        self.onLogin(request.form.get('username', ''), request.form.get('password', ''))
        return self.rendered_page

    def onLogin(self, username: str, password: str) -> None:
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
        self.rendered_page = redirect(url_for('dashboard'))

    def displayError(self) -> None:
        self.rendered_page = (render_template('auth/login.html',
            values={'username': request.form.get('username', '')}, errors=self.field_errors,
            title='User Admin Login', login_role='admin', error_message=self.error_message), 400)
