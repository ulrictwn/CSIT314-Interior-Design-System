# control/designer/project_interest_controller.py: provides the controller used to communicate with its entity.
from control.designer.project_interest_controller import ProjectInterestController
# boundary/validation.py: trims ordinary text before the entity call.
from boundary.validation import strip_input
# infrastructure/errors.py: defines expected validation, missing-record and access errors.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/portal.py: formats customer, designer-interest and manager portal responses.
from boundary.portal import present, error_response
# control/designer/view_count_controller.py: provides the controller used to communicate with its entity.
from control.designer.view_count_controller import ViewCountController


class ViewCountPage(MethodView):
    def get(self,project_id):
        """Pass the URL project ID to onView() and return its prepared response."""
        self.onView(project_id)
        return self.rendered_page

    def onView(self,projectId: int) -> None:
        """Strip the project ID and request its saved count through the entity controllers."""
        try:
            projectId = strip_input(projectId)
            self.project = ProjectInterestController().getProject(projectId)
        except DomainError as error:
            self.rendered_page = error_response(str(error), 'designer', {'projectId': [str(error)]})
            return
        controller = ViewCountController()
        if self.project is None:
            self.rendered_page = error_response('Project not found.','designer',status=404)
            return
        self.displayViewCount(controller.getViewCount(projectId))

    def displayViewCount(self,viewCount: int) -> None:
        """Display the project and its view count using boundary/portal.py."""
        self.rendered_page = present(dict(ok=True,metric='viewCount',count=viewCount,project=self.project.as_public_dict()),
            'interest/detail.html','Project Views','designer')
