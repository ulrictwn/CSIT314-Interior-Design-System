from flask import session, url_for
from flask.views import MethodView
# boundary/designer/presentation.py: chooses designer HTML/JSON responses.
from boundary.designer.presentation import present


class InteriorDesignerDashboardPage(MethodView):
    def get(self):
        """Display the designer dashboard with links for the signed-in account."""
        return present(dict(ok=True, accountId=session.get('account_id'), links={
            'company': url_for('view_company_profile'),
            'newProjects': url_for('new_projects'),
            'pastProjects': url_for('past_projects'),
        }))
