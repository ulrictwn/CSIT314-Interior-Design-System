from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.validation import PROJECT_FIELDS, validate_project_fields, positive_integer, project_values
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.projects.update_new_project_controller import UpdateNewProjectController
from infrastructure.errors import DomainError


class UpdateNewProjectPage(MethodView):
    def get(self, project_id):
        try:
            projectId = positive_integer(project_id, 'Project ID')
        except DomainError as error:
            return error_response(str(error), {'projectId': [str(error)]})
        project = UpdateNewProjectController().getNewProject(projectId)
        if project is None:
            return error_response('New project not found.', status=404)
        return present(dict(ok=True, fields=PROJECT_FIELDS, project=project_values(project), values=project_values(project)))

    def post(self, project_id):
        values = request_values()
        self.onUpdate(project_id, *(values.get(field, '') for field in PROJECT_FIELDS))
        return self.rendered_page

    def onUpdate(self, projectId: int, projectName: str, categoryId: int, propertyType: str,
                 area: str, renovationCost: float, description: str) -> None:
        self.values = dict(zip(PROJECT_FIELDS, [projectName, categoryId, propertyType, area, renovationCost, description]))
        self.values['renovationCost'] = str(renovationCost) if renovationCost is not None else ''
        values, self.field_errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        self.error_reason = 'invalid_data'
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.field_errors['projectId'] = [str(error)]
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            self.displayError()
            return
        controller = UpdateNewProjectController()
        if controller.updateNewProject(projectId, **values):
            self.values = values
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.error_message, controller.field_errors
            self.error_reason = controller.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='New project updated successfully.', values=self.values), 200)

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
