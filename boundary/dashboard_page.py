from flask import g, render_template, redirect, url_for
from flask.views import MethodView
# infrastructure/navigation.py: builds sidebar links and selects role dashboards.
from infrastructure.navigation import dashboard_endpoint


class HomePage(MethodView):
    def get(self):
        """Open the signed-in account's dashboard or the login page."""
        if g.current_user:
            return redirect(url_for(dashboard_endpoint(g.current_user)))
        return redirect(url_for('login'))


class DashboardPage(MethodView):
    def get(self):
        """Display the User Admin dashboard."""
        return render_template('dashboard.html', title='User Admin Dashboard')
