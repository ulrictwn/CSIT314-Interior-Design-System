from flask import request
from flask.views import MethodView
from boundary.designer.context import account_id
from boundary.portal import present, error_response
from control.designer.project_interest_controller import ProjectInterestController
from infrastructure.errors import DomainError


class ProjectInterestPage(MethodView):
    def get(self,metric):
        try:
            owner = account_id()
        except DomainError as error:
            return error_response(str(error),'designer')
        return present(dict(ok=True,metric=metric,projects=ProjectInterestController().projects(owner)),
            'interest/index.html','Project '+('Views' if metric == 'views' else 'Shortlists'),'designer')
