from flask import session, flash, redirect, url_for
from flask.views import MethodView
# boundary/designer/presentation.py: chooses designer HTML/JSON responses.
from boundary.designer.presentation import wants_html


class LogoutPage(MethodView):
    def post(self):
        """Handle the logout form and return the response prepared by logout()."""
        self.logout()
        return self.rendered_page

    def logout(self) -> None:
        """Clear the browser session and call displayLoginPage()."""
        session.clear()
        self.displayLoginPage()

    def displayLoginPage(self) -> None:
        """Show the sign-out message and redirect to the admin login page."""
        if wants_html():
            flash('You have signed out successfully.', 'success')
        self.rendered_page = redirect(url_for('login'))
