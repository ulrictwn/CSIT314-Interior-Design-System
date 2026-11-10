from flask.views import MethodView
# boundary/designer/context.py: reads form/JSON values and the signed-in account.
from boundary.designer.context import account_id
# boundary/portal.py: formats customer, designer-interest and manager portal responses.
from boundary.portal import present
# control/designer/project_interest_controller.py: provides the controller used to communicate with its entity.
from control.designer.project_interest_controller import ProjectInterestController


class ProjectInterestPage(MethodView):
    def get(self,metric):
        """Display the designer's project counts through control/designer/project_interest_controller.py."""
        owner = account_id()
        return present(dict(ok=True,metric=metric,projects=ProjectInterestController().projects(owner)),
            'interest/index.html','Project '+('Views' if metric == 'views' else 'Shortlists'),'designer')
