from boundary.validation import strip_input
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.projects.presentation import project_values
from boundary.designer.responses import error_response
from control.projects.view_new_project_controller import ViewNewProjectController
from entity.projects.interior_design_project import InteriorDesignProject


class ViewNewProjectPage(MethodView):
    def get(self, project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self, projectId: int) -> None:
        projectId = strip_input(projectId)
        project = ViewNewProjectController().getNewProject(projectId)
        if project is None:
            self.rendered_page = error_response('New project not found.', status=404)
        else:
            self.displayProject(project)

    def displayProject(self, project: InteriorDesignProject) -> None:
        self.rendered_page = present(dict(ok=True, project=project_values(project)), 200)
