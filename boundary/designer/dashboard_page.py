from flask import session, url_for
from flask.views import MethodView
from boundary.designer.presentation import present


class InteriorDesignerDashboardPage(MethodView):
    def get(self):
        return present(dict(ok=True, accountId=session.get('account_id'), links={
            'company': url_for('view_company_profile'),
            'newProjects': url_for('new_projects'),
            'pastProjects': url_for('past_projects'),
        }))
