from flask import flash, redirect, session, url_for
from flask.views import MethodView
from boundary.designer.presentation import wants_html


class LogoutPage(MethodView):
    def post(self):
        self.logout()
        return self.rendered_page

    def logout(self) -> None:
        session.clear()
        self.displayLoginPage()

    def displayLoginPage(self) -> None:
        if wants_html():
            flash('You have signed out successfully.','success')
        self.rendered_page = redirect(url_for('customer_login'))
