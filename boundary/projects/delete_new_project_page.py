# control/projects/view_new_project_controller.py: controller used to relay this page's entity requests.
from control.projects.view_new_project_controller import ViewNewProjectController
# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
# infrastructure/errors.py: application error types.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/projects/presentation.py: project form fields and display values.
from boundary.projects.presentation import project_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response, entity_error
# control/projects/delete_new_project_controller.py: controller used to relay this page's entity requests.
from control.projects.delete_new_project_controller import DeleteNewProjectController


class DeleteNewProjectPage(MethodView):
    def get(self, project_id):
        """Retrieve existing details through the View controller and ask for confirmation."""
        try:
            project = ViewNewProjectController().getNewProject(strip_input(project_id))
        except DomainError as error:
            return error_response(str(error), {'projectId': [str(error)]})
        if project is None:
            return error_response('New project not found.', status=404)
        return present(dict(ok=True, confirmationRequired=True, project=project_values(project)))

    def post(self, project_id):
        """Read the submitted input, call onDelete, and return the prepared response."""
        self.onDelete(project_id)
        return self.rendered_page

    def onDelete(self, projectId: int) -> None:
        """Call the imported deletion controller and display success or saved-data errors."""
        projectId = strip_input(projectId)
        controller = DeleteNewProjectController()
        if controller.deleteNewProject(projectId):
            self.displaySuccess()
        else:
            self.rendered_page = entity_error(controller)

    def displaySuccess(self) -> None:
        """Display the successful operation through the imported present helper."""
        self.rendered_page = present(dict(ok=True, message='New project deleted successfully.'), 200)
