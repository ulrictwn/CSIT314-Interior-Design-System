# control/projects/view_past_project_controller.py: controller used to relay this page's entity requests.
from control.projects.view_past_project_controller import ViewPastProjectController
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
from boundary.designer.responses import error_response, entity_error
# control/projects/delete_past_project_controller.py: controller used to relay this page's entity requests.
from control.projects.delete_past_project_controller import DeletePastProjectController


class DeletePastProjectPage(MethodView):
    def get(self, project_id):
        """Retrieve existing details through the View controller and ask for confirmation."""
        try:
            projectId = positive_integer(strip_input(project_id), 'Project ID')
        except DomainError as error:
            return error_response(str(error), {'projectId': [str(error)]})
        project = ViewPastProjectController().getPastProject(projectId)
        if project is None:
            return error_response('Past project not found.', status=404)
        return present(dict(ok=True, confirmationRequired=True, project=project_values(project)))

    def post(self, project_id):
        """Read the submitted input, call onDelete, and return the prepared response."""
        self.onDelete(project_id)
        return self.rendered_page

    def onDelete(self, projectId: int) -> None:
        """Call the imported deletion controller and display success or saved-data errors."""
        try:
            projectId = positive_integer(strip_input(projectId), 'Project ID')
        except DomainError as error:
            self.rendered_page = error_response(str(error), {'projectId': [str(error)]})
            return
        controller = DeletePastProjectController()
        if controller.deletePastProject(projectId):
            self.displaySuccess()
        else:
            self.rendered_page = entity_error(controller)

    def displaySuccess(self) -> None:
        """Display the successful operation through the imported present helper."""
        self.rendered_page = present(dict(ok=True, message='Past project deleted successfully.'), 200)
