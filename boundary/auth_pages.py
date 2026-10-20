from flask import g, session, flash, redirect, url_for, request, render_template
from flask.views import MethodView
from boundary.base import Page
from boundary.forms import LoginForm, ActionForm
from control.auth_controller import LoginController, LogoutController
from infrastructure.auth import safe_next, establish_session
from infrastructure.errors import DomainError


class LoginPage(MethodView):
    def get(self):
        if g.current_user:
            return redirect(url_for('dashboard'))
        return render_template('auth/login.html', form=LoginForm(), title='User Admin Login')

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            try:
                self.clickLogin(form.username.data, form.password.data)
                return self.rendered_page
            except DomainError as error:
                flash(str(error), 'error')
        self.displayError(form)
        return self.rendered_page

    def clickLogin(self, username, password) -> None:
        controller = LoginController()
        controller.login(username, password, request.remote_addr or '')
        establish_session(controller.account)
        self.displayDashboard()

    def displayDashboard(self) -> None:
        self.rendered_page = redirect(safe_next(request.args.get('next')))

    def displayError(self, form=None) -> None:
        self.rendered_page = (render_template('auth/login.html', form=form if form is not None else LoginForm(), title='User Admin Login'), 400)


class LogoutPage(Page):
    def post(self):
        if not ActionForm().validate_on_submit():
            raise DomainError('Reload the page and try again.')
        self.logout()
        return self.rendered_page

    def logout(self) -> None:
        LogoutController().logout(session)
        self.displayLoginPage()

    def displayLoginPage(self) -> None:
        self.rendered_page = redirect(url_for('login'))
