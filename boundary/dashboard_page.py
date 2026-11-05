from flask import g, render_template, redirect, url_for
from flask.views import MethodView


class HomePage(MethodView):
    def get(self):
        if g.current_user:
            return redirect(url_for('designer_dashboard' if g.current_user.profile.name.casefold() == 'interior designer' else 'dashboard'))
        return redirect(url_for('login'))


class DashboardPage(MethodView):
    def get(self):
        return render_template('dashboard.html', title='User Admin Dashboard')
