# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/projects/presentation.py: project form fields and display values.
from boundary.projects.presentation import PROJECT_FIELDS, project_values
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import account_id, request_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/projects/create_past_project_controller.py: controller used to relay this page's entity requests.
from control.projects.create_past_project_controller import CreatePastProjectController


class CreatePastProjectPage(MethodView):
    def get(self):
        """Display an empty form through the imported present helper."""
        return present(dict(ok=True, fields=PROJECT_FIELDS, values={}))

    def post(self):
        """Read the submitted input, call onCreate, and return the prepared response."""
        values = request_values()
        self.onCreate(*(values.get(field, '') for field in PROJECT_FIELDS))
        return self.rendered_page

    def onCreate(self, projectName: str, categoryId: int, propertyType: str,
                 area: str, renovationCost: float, description: str) -> None:
        """Strip entered text, then ask the controller/entity to validate and save it."""
        self.values = {field: strip_input(value) for field, value in zip(PROJECT_FIELDS,
            [projectName, categoryId, propertyType, area, renovationCost, description])}
        controller = CreatePastProjectController()
        if controller.createPastProject(account_id(), **self.values):
            self.project = controller.entity
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        """Display the successful operation through the imported present helper."""
        self.rendered_page = present(dict(ok=True, message='Past project created successfully.', project=project_values(self.project)), 201)

    def displayError(self) -> None:
        """Display field or saved-data errors with the submitted values."""
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
