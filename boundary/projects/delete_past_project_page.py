from control.projects.view_past_project_controller import ViewPastProjectController
from boundary.validation import strip_input
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.presentation import project_values
from boundary.designer.responses import error_response, entity_error
from control.projects.delete_past_project_controller import DeletePastProjectController


class DeletePastProjectPage(MethodView):
    def get(self, project_id):
        projectId = strip_input(project_id)
        project = ViewPastProjectController().getPastProject(projectId)
        if project is None:
            return error_response('Past project not found.', status=404)
        return present(dict(ok=True, confirmationRequired=True, project=project_values(project)))

    def post(self, project_id):
        self.onDelete(project_id)
        return self.rendered_page

    def onDelete(self, projectId: int) -> None:
        projectId = strip_input(projectId)
        controller = DeletePastProjectController()
        if controller.deletePastProject(projectId):
            self.displaySuccess()
        else:
            self.rendered_page = entity_error(controller)

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='Past project deleted successfully.'), 200)
