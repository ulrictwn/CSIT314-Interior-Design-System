from control.designer.project_interest_controller import ProjectInterestController
from boundary.validation import strip_input
from flask.views import MethodView
from boundary.portal import present, error_response
from control.designer.view_shortlist_count_controller import ViewShortlistCountController


class ViewShortlistCountPage(MethodView):
    def get(self,project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self,projectId: int) -> None:
        projectId = strip_input(projectId)
        controller = ViewShortlistCountController()
        self.project = ProjectInterestController().getProject(projectId)
        if self.project is None:
            self.rendered_page = error_response('Project not found.','designer',status=404)
            return
        self.displayShortlistCount(controller.getShortlistCount(projectId))

    def displayShortlistCount(self,shortlistCount: int) -> None:
        self.rendered_page = present(dict(ok=True,metric='shortlistCount',count=shortlistCount,project=self.project.as_public_dict()),
            'interest/detail.html','Project Shortlists','designer')
