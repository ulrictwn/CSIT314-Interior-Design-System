from flask.views import MethodView
from boundary.projects.validation import positive_integer
from boundary.portal import present, error_response
from control.designer.view_count_controller import ViewCountController
from infrastructure.errors import DomainError


class ViewCountPage(MethodView):
    def get(self,project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self,projectId: int) -> None:
        try:
            projectId = positive_integer(projectId,'Project ID')
        except DomainError as error:
            self.rendered_page = error_response(str(error),'designer')
            return
        controller = ViewCountController()
        self.project = controller.getProject(projectId)
        if self.project is None:
            self.rendered_page = error_response('Project not found.','designer',status=404)
            return
        self.displayViewCount(controller.getViewCount(projectId))

    def displayViewCount(self,viewCount: int) -> None:
        self.rendered_page = present(dict(ok=True,metric='viewCount',count=viewCount,project=self.project.as_public_dict()),
            'interest/detail.html','Project Views','designer')
