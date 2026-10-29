from flask import render_template, g, redirect, url_for
from flask.views import MethodView
from boundary.base import Page
from infrastructure.database import db
from entity.profile.user_profile import UserProfile
from entity.accounts.user_account import UserAccount


class HomePage(MethodView):
    def get(self):
        return redirect(url_for('dashboard' if g.current_user else 'login'))


class DashboardPage(Page):
    def get(self):
        cards = []
        if self.actor.has_permission('profile.view'):
            cards.append(('User profiles', db.session.scalar(db.select(db.func.count()).select_from(UserProfile)), 'user_profiles'))
        if self.actor.has_permission('account.view'):
            cards.append(('User accounts', db.session.scalar(db.select(db.func.count()).select_from(UserAccount)), 'user_accounts'))
        return render_template('dashboard.html', cards=cards, title='User Admin Dashboard')
