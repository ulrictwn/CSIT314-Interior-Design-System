# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import optional_account_id, present, error_response
# control/customer/view_idp_controller.py: the boundary-to-entity request handler.
from control.customer.view_idp_controller import ViewIDPController
# control/customer/dashboard_controller.py: the boundary-to-entity request handler.
from control.customer.dashboard_controller import CustomerDashboardController
# entity/projects/interior_design_project.py: saved project data.
from entity.projects.interior_design_project import InteriorDesignProject


class ViewIDPPage(MethodView):
    def get(self, project_id):
        """Receive the project URL and run the diagram onView event."""
        self.onView(project_id)
        return self.rendered_page

    def onView(self, projectId: int) -> None:
        """Strip the supplied ID and display details or the entity validation error."""
        self.owner = optional_account_id()
        try:
            idp = ViewIDPController().getIDP(strip_input(projectId))
        except DomainError as error:
            self.rendered_page = error_response(str(error), 'customer', {'projectId': [str(error)]})
            return
        if idp is None:
            self.rendered_page = error_response('Project not found.','customer',status=404)
            return
        self.displayIDP(idp)

    def displayIDP(self, idp: InteriorDesignProject) -> None:
        """Display the project details and the customer's shortlist state."""
        self.rendered_page = present(dict(ok=True, project=idp.as_public_dict(),
            savedIds=CustomerDashboardController().savedProjectIds(self.owner), shortlisted=False),
            'customer/project.html', 'View Project Details', 'customer')
