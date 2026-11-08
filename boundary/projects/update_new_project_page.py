from boundary.validation import strip_input
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.presentation import PROJECT_FIELDS, project_values
from boundary.designer.context import request_values
from boundary.designer.responses import error_response
from control.projects.update_new_project_controller import UpdateNewProjectController


class UpdateNewProjectPage(MethodView):
    def get(self, project_id):
        projectId = strip_input(project_id)
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
        self.values = {field: strip_input(value) for field, value in zip(PROJECT_FIELDS,
            [projectName, categoryId, propertyType, area, renovationCost, description])}
        controller = UpdateNewProjectController()
        if controller.updateNewProject(projectId, **self.values):
            self.values = project_values(controller.getNewProject(projectId))
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='New project updated successfully.', values=self.values), 200)

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
