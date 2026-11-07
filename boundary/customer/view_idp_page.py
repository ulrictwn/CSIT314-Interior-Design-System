from flask.views import MethodView
from boundary.projects.validation import positive_integer
from boundary.designer.context import account_id
from boundary.portal import optional_account_id, present, error_response
from control.customer.view_idp_controller import ViewIDPController
from control.customer.dashboard_controller import CustomerDashboardController
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.errors import DomainError


class ViewIDPPage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self, project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self, projectId: int) -> None:
        try:
            projectId = positive_integer(projectId,'Project ID')
            self.owner = optional_account_id()
        except DomainError as error:
            self.rendered_page = error_response(str(error),'customer')
            return
        idp = ViewIDPController().getIDP(projectId)
        if idp is None:
            self.rendered_page = error_response('Project not found.','customer',status=404)
            return
        self.displayIDP(idp)

    def displayIDP(self, idp: InteriorDesignProject) -> None:
        self.rendered_page = present(dict(ok=True, project=idp.as_public_dict(),
            savedIds=CustomerDashboardController().savedProjectIds(self.owner), shortlisted=False),
            'customer/project.html', 'View Project Details', 'customer')
