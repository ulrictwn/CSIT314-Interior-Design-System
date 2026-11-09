from boundary.validation import strip_input
from flask.views import MethodView
from boundary.portal import optional_account_id, present, error_response
from control.customer.view_idp_controller import ViewIDPController
from control.customer.dashboard_controller import CustomerDashboardController
from entity.projects.interior_design_project import InteriorDesignProject


class ViewIDPPage(MethodView):
    def get(self, project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self, projectId: int) -> None:
        projectId = strip_input(projectId)
        self.owner = optional_account_id()
        idp = ViewIDPController().getIDP(projectId)
        if idp is None:
            self.rendered_page = error_response('Project not found.','customer',status=404)
            return
        self.displayIDP(idp)

    def displayIDP(self, idp: InteriorDesignProject) -> None:
        self.rendered_page = present(dict(ok=True, project=idp.as_public_dict(),
            savedIds=CustomerDashboardController().savedProjectIds(self.owner), shortlisted=False),
            'customer/project.html', 'View Project Details', 'customer')
