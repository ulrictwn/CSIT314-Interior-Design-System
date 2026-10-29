from flask import session, redirect, url_for
from boundary.base import Page
from control.auth.logout_controller import LogoutController


class LogoutPage(Page):
    def post(self):
        self.logout()
        return self.rendered_page

    def logout(self) -> None:
        LogoutController().logout(session.get('session_token'))
        session.clear()
        self.displayLoginPage()

    def displayLoginPage(self) -> None:
        self.rendered_page = redirect(url_for('login'))
