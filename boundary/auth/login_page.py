from flask import current_app, g, session, flash, redirect, url_for, request, render_template
from flask.views import MethodView
from control.auth.login_controller import LoginController
from infrastructure.auth import safe_next


class LoginPage(MethodView):
    def get(self):
        if g.current_user:
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html', values={}, errors={}, title='User Admin Login')

    def post(self):
        self.clickLogin(request.form.get('username', ''), request.form.get('password', ''))
        return self.rendered_page

    def clickLogin(self, username: str, password: str) -> None:
        controller = LoginController(remote_address=request.remote_addr or '',
            attempt_limit=current_app.config['LOGIN_ATTEMPT_LIMIT'],
            previous_token=session.get('session_token'),
            session_lifetime=current_app.permanent_session_lifetime)
        if controller.login(username, password):
            session.clear()
            session.update(controller.session_data)
            session.permanent = True
            self.displayDashboard()
        else:
            self.error_message = controller.error_message
            self.field_errors = controller.field_errors
            self.displayError()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(safe_next(request.args.get('next')))

    def displayError(self) -> None:
        flash(self.error_message, 'error')
        self.rendered_page = (render_template('auth/login.html',
            values={'username': request.form.get('username', '')}, errors=self.field_errors,
            title='User Admin Login'), 400)
