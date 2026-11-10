from flask import flash, redirect, session, url_for
from flask.views import MethodView
# boundary/designer/presentation.py: HTML or JSON presentation choice.
from boundary.designer.presentation import wants_html


class PlatformManagerLogoutPage(MethodView):
    def post(self):
        """Read the submitted request, run logout, and return the prepared response."""
        self.logout()
        return self.rendered_page

    def logout(self) -> None:
        """Clear the browser session and display the login page."""
        session.clear()
        self.displayLoginPage()

    def displayLoginPage(self) -> None:
        """Prepare the redirect to this portal's login page."""
        if wants_html():
            flash('You have signed out successfully.','success')
        self.rendered_page = redirect(url_for('platform_manager_login'))
