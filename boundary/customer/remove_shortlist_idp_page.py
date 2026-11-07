from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import account_id
from boundary.designer.presentation import wants_html
from boundary.projects.validation import positive_integer
from boundary.portal import error_response
from control.customer.remove_shortlist_idp_controller import RemoveShortlistIDPController
from infrastructure.errors import DomainError


class RemoveShortlistIDPPage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def post(self, project_id):
        self.onRemove(project_id)
        return self.rendered_page

    def onRemove(self, projectId: int) -> None:
        try:
            self.projectId = positive_integer(projectId,'Project ID')
            self.owner = account_id(self.accountId)
        except DomainError as error:
            self.error_message, self.status = str(error), 400
            self.displayError()
            return
        controller = RemoveShortlistIDPController()
        if controller.removeShortlist(self.owner,self.projectId):
            self.displaySuccess()
        else:
            self.error_message = controller.error_message
            self.status = 404 if controller.error_reason == 'not_found' else 400
            self.displayError()

    def displaySuccess(self) -> None:
        if wants_html():
            flash('Project removed from your shortlist.','success')
            self.rendered_page = redirect(url_for('search_shortlist_idps', accountId=self.owner), code=303)
        else:
            self.rendered_page = dict(ok=True,message='Project removed from your shortlist.',projectId=self.projectId), 200

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message,'customer',status=self.status)
