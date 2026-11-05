from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.validation import PROJECT_FIELDS, validate_project_fields, positive_integer, project_values
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.projects.create_past_project_controller import CreatePastProjectController
from infrastructure.errors import DomainError


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
        self.values = dict(zip(PROJECT_FIELDS, [projectName, categoryId, propertyType, area, renovationCost, description]))
        self.values['renovationCost'] = str(renovationCost) if renovationCost is not None else ''
        values, self.field_errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        self.error_reason = 'invalid_data'
        try:
            accountId = account_id(self.accountId)
        except DomainError as error:
            self.field_errors['accountId'] = [str(error)]
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            self.displayError()
            return
        controller = CreatePastProjectController()
        if controller.createPastProject(accountId, **values):
            self.values = values
            self.project = controller.project
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.error_message, controller.field_errors
            self.error_reason = controller.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='Past project created successfully.', project=project_values(self.project)), 201)

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
