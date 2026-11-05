from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.validation import positive_integer, project_values
from boundary.designer.responses import error_response
from control.projects.view_past_project_controller import ViewPastProjectController
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.errors import DomainError


class ViewPastProjectPage(MethodView):
    def get(self, project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self, projectId: int) -> None:
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.rendered_page = error_response(str(error), {'projectId': [str(error)]})
            return
        project = ViewPastProjectController().getPastProject(projectId)
        if project is None:
            self.rendered_page = error_response('Past project not found.', status=404)
        else:
            self.displayProject(project)

    def displayProject(self, project: InteriorDesignProject) -> None:
        self.rendered_page = present(dict(ok=True, project=project_values(project)), 200)
