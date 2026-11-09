from control.designer.project_interest_controller import ProjectInterestController
from boundary.validation import strip_input
from flask.views import MethodView
from boundary.portal import present, error_response
from control.designer.view_count_controller import ViewCountController


class ViewCountPage(MethodView):
    def get(self,project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self,projectId: int) -> None:
        projectId = strip_input(projectId)
        controller = ViewCountController()
        self.project = ProjectInterestController().getProject(projectId)
        if self.project is None:
            self.rendered_page = error_response('Project not found.','designer',status=404)
            return
        self.displayViewCount(controller.getViewCount(projectId))

    def displayViewCount(self,viewCount: int) -> None:
        self.rendered_page = present(dict(ok=True,metric='viewCount',count=viewCount,project=self.project.as_public_dict()),
            'interest/detail.html','Project Views','designer')
