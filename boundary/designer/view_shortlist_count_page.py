from flask.views import MethodView
from boundary.projects.validation import positive_integer
from boundary.portal import present, error_response
from control.designer.view_shortlist_count_controller import ViewShortlistCountController
from infrastructure.errors import DomainError


class ViewShortlistCountPage(MethodView):
    def get(self,project_id):
        self.onView(project_id)
        return self.rendered_page

    def onView(self,projectId: int) -> None:
        try:
            projectId = positive_integer(projectId,'Project ID')
        except DomainError as error:
            self.rendered_page = error_response(str(error),'designer')
            return
        controller = ViewShortlistCountController()
        self.project = controller.getProject(projectId)
        if self.project is None:
            self.rendered_page = error_response('Project not found.','designer',status=404)
            return
        self.displayShortlistCount(controller.getShortlistCount(projectId))

    def displayShortlistCount(self,shortlistCount: int) -> None:
        self.rendered_page = present(dict(ok=True,metric='shortlistCount',count=shortlistCount,project=self.project.as_public_dict()),
            'interest/detail.html','Project Shortlists','designer')
