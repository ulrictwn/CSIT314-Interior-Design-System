from flask import g, render_template, redirect, url_for
from flask.views import MethodView
from infrastructure.navigation import dashboard_endpoint


class HomePage(MethodView):
    def get(self):
        if g.current_user:
            return redirect(url_for(dashboard_endpoint(g.current_user)))
        return redirect(url_for('login'))


class DashboardPage(MethodView):
    def get(self):
        return render_template('dashboard.html', title='User Admin Dashboard')
