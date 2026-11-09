from boundary.validation import strip_input
from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import account_id
from boundary.designer.presentation import wants_html
from boundary.portal import error_response
from control.customer.save_shortlist_idp_controller import SaveShortlistIDPController


class SaveShortlistIDPPage(MethodView):
    def post(self, project_id):
        self.onSave(project_id)
        return self.rendered_page

    def onSave(self, projectId: int) -> None:
        self.projectId = strip_input(projectId)
        self.owner = account_id()
        controller = SaveShortlistIDPController()
        if controller.saveShortlist(self.owner,self.projectId):
            self.displaySuccess()
        else:
            self.error_message = controller.entity.error_message
            self.status = 404 if controller.entity.error_reason == 'not_found' else 400
            self.displayError()

    def displaySuccess(self) -> None:
        if wants_html():
            flash('Project saved to your shortlist.','success')
            self.rendered_page = redirect(url_for('view_idp', accountId=self.owner, project_id=self.projectId), code=303)
        else:
            self.rendered_page = dict(ok=True,message='Project saved to your shortlist.',projectId=self.projectId), 201

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message,'customer',status=self.status)
