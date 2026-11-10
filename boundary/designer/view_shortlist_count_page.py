# control/designer/project_interest_controller.py: provides the controller used to communicate with its entity.
from control.designer.project_interest_controller import ProjectInterestController
# boundary/validation.py: trims and checks submitted input fields.
from boundary.validation import strip_input, positive_integer
# infrastructure/errors.py: defines expected validation, missing-record and access errors.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/portal.py: formats customer, designer-interest and manager portal responses.
from boundary.portal import present, error_response
# control/designer/view_shortlist_count_controller.py: provides the controller used to communicate with its entity.
from control.designer.view_shortlist_count_controller import ViewShortlistCountController


class ViewShortlistCountPage(MethodView):
    def get(self,project_id):
        """Pass the URL project ID to onView() and return its prepared response."""
        self.onView(project_id)
        return self.rendered_page

    def onView(self,projectId: int) -> None:
        """Check the project ID, then request its count from ViewShortlistCountController."""
        try:
            projectId = positive_integer(strip_input(projectId), 'Project ID')
        except DomainError as error:
            self.rendered_page = error_response(str(error), 'designer', {'projectId': [str(error)]})
            return
        controller = ViewShortlistCountController()
        self.project = ProjectInterestController().getProject(projectId)
        if self.project is None:
            self.rendered_page = error_response('Project not found.','designer',status=404)
            return
        self.displayShortlistCount(controller.getShortlistCount(projectId))

    def displayShortlistCount(self,shortlistCount: int) -> None:
        """Display the project and its shortlist count using boundary/portal.py."""
        self.rendered_page = present(dict(ok=True,metric='shortlistCount',count=shortlistCount,project=self.project.as_public_dict()),
            'interest/detail.html','Project Shortlists','designer')
