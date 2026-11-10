# control/projects/view_new_project_controller.py: controller used to relay this page's entity requests.
from control.projects.view_new_project_controller import ViewNewProjectController
# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, positive_integer, validate_project_fields
# infrastructure/errors.py: application error types.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/projects/presentation.py: project form fields and display values.
from boundary.projects.presentation import PROJECT_FIELDS, project_values
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import request_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/projects/update_new_project_controller.py: controller used to relay this page's entity requests.
from control.projects.update_new_project_controller import UpdateNewProjectController


class UpdateNewProjectPage(MethodView):
    def get(self, project_id):
        """Retrieve existing details through the View controller and prefill the form."""
        try:
            projectId = positive_integer(strip_input(project_id), 'Project ID')
        except DomainError as error:
            return error_response(str(error), {'projectId': [str(error)]})
        project = ViewNewProjectController().getNewProject(projectId)
        if project is None:
            return error_response('New project not found.', status=404)
        return present(dict(ok=True, fields=PROJECT_FIELDS, project=project_values(project), values=project_values(project)))

    def post(self, project_id):
        """Read the submitted input, call onUpdate, and return the prepared response."""
        values = request_values()
        self.onUpdate(project_id, *(values.get(field, '') for field in PROJECT_FIELDS))
        return self.rendered_page

    def onUpdate(self, projectId: int, projectName: str, categoryId: int, propertyType: str,
                 area: str, renovationCost: float, description: str) -> None:
        """Validate entered fields, then call the imported controller and display its result."""
        self.values = {field: strip_input(value) for field, value in zip(PROJECT_FIELDS,
            [projectName, categoryId, propertyType, area, renovationCost, description])}
        values, self.field_errors = validate_project_fields(**self.values)
        try:
            projectId = positive_integer(strip_input(projectId), 'Project ID')
        except DomainError as error:
            self.field_errors['projectId'] = [str(error)]
        if self.field_errors:
            self.error_message, self.error_reason = 'Please correct the errors below.', 'invalid_data'
            self.displayError()
            return
        self.values = values
        controller = UpdateNewProjectController()
        if controller.updateNewProject(projectId, **self.values):
            self.values = project_values(ViewNewProjectController().getNewProject(projectId))
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        """Display the successful operation through the imported present helper."""
        self.rendered_page = present(dict(ok=True, message='New project updated successfully.', values=self.values), 200)

    def displayError(self) -> None:
        """Display field or saved-data errors with the submitted values."""
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
