# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
from flask import flash, redirect, url_for
from flask.views import MethodView
# boundary/designer/context.py: submitted values and signed-in account context.
from boundary.designer.context import account_id
# boundary/designer/presentation.py: HTML or JSON presentation choice.
from boundary.designer.presentation import wants_html
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import error_response
# control/customer/remove_shortlist_idp_controller.py: the boundary-to-entity request handler.
from control.customer.remove_shortlist_idp_controller import RemoveShortlistIDPController


class RemoveShortlistIDPPage(MethodView):
    def post(self, project_id):
        """Read the submitted request, run onRemove, and return the prepared response."""
        self.onRemove(project_id)
        return self.rendered_page

    def onRemove(self, projectId: int) -> None:
        """Strip the project ID and display the shortlist result or entity error."""
        self.projectId = strip_input(projectId)
        self.owner = account_id()
        controller = RemoveShortlistIDPController()
        if controller.removeShortlist(self.owner,self.projectId):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.status = 404 if controller.entity.error_reason == 'not_found' else 400
            self.displayError()

    def displaySuccess(self) -> None:
        """Display the successful operation result or prepare its redirect."""
        if wants_html():
            flash('Project removed from your shortlist.','success')
            self.rendered_page = redirect(url_for('search_shortlist_idps', accountId=self.owner), code=303)
        else:
            self.rendered_page = dict(ok=True,message='Project removed from your shortlist.',projectId=self.projectId), 200

    def displayError(self) -> None:
        """Display the input or saved-data error returned by this operation."""
        self.rendered_page = error_response(self.error_message,'customer',status=self.status)
