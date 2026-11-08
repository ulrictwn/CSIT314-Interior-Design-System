from boundary.validation import strip_input
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.presentation import PROJECT_FIELDS, project_values
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.projects.create_past_project_controller import CreatePastProjectController


class CreatePastProjectPage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        return present(dict(ok=True, fields=PROJECT_FIELDS, values={}))

    def post(self):
        values = request_values()
        self.onCreate(*(values.get(field, '') for field in PROJECT_FIELDS))
        return self.rendered_page

    def onCreate(self, projectName: str, categoryId: int, propertyType: str,
                 area: str, renovationCost: float, description: str) -> None:
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
        self.rendered_page = present(dict(ok=True, message='Past project created successfully.', project=project_values(self.project)), 201)

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
