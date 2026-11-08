from flask import request
from flask.views import MethodView
from boundary.designer.context import account_id
from boundary.portal import present
from control.designer.project_interest_controller import ProjectInterestController


class ProjectInterestPage(MethodView):
    def get(self,metric):
        owner = account_id()
        return present(dict(ok=True,metric=metric,projects=ProjectInterestController().projects(owner)),
            'interest/index.html','Project '+('Views' if metric == 'views' else 'Shortlists'),'designer')
