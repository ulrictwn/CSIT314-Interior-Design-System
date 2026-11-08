from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.company.presentation import company_values
from boundary.designer.context import account_id
from boundary.designer.responses import error_response, entity_error
from control.company.delete_company_profile_controller import DeleteCompanyProfileController


class DeleteCompanyProfilePage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        accountId = account_id(self.accountId)
        profile = DeleteCompanyProfileController().getCompanyProfile(accountId)
        if profile is None:
            return error_response('Company profile not found.', status=404)
        return present(dict(ok=True, confirmationRequired=True, profile=company_values(profile)))

    def post(self):
        self.onDelete()
        return self.rendered_page

    def onDelete(self) -> None:
        accountId = account_id(self.accountId)
        controller = DeleteCompanyProfileController()
        if controller.deleteCompanyProfile(accountId):
            self.displaySuccess()
        else:
            self.rendered_page = entity_error(controller)

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='Company profile deleted successfully.'), 200)
