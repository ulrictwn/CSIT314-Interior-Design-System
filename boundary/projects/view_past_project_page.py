# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, positive_integer
# infrastructure/errors.py: application error types.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/projects/presentation.py: project form fields and display values.
from boundary.projects.presentation import project_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/projects/view_past_project_controller.py: controller used to relay this page's entity requests.
from control.projects.view_past_project_controller import ViewPastProjectController
# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class ViewPastProjectPage(MethodView):
    def get(self, project_id):
        """Open the selected record through the diagram onView method."""
        self.onView(project_id)
        return self.rendered_page

    def onView(self, projectId: int) -> None:
        """Retrieve the selected record through the imported View controller."""
        try:
            projectId = positive_integer(strip_input(projectId), 'Project ID')
        except DomainError as error:
            self.rendered_page = error_response(str(error), {'projectId': [str(error)]})
            return
        project = ViewPastProjectController().getPastProject(projectId)
        if project is None:
            self.rendered_page = error_response('Past project not found.', status=404)
        else:
            self.displayProject(project)

    def displayProject(self, project: InteriorDesignProject) -> None:
        """Prepare the retrieved details for the imported HTML/JSON presenter."""
        self.rendered_page = present(dict(ok=True, project=project_values(project)), 200)
