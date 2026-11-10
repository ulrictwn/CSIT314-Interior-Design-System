# control/company/view_company_profile_controller.py: controller used to relay this page's entity requests.
from control.company.view_company_profile_controller import ViewCompanyProfileController
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/company/presentation.py: company form fields and display values.
from boundary.company.presentation import company_values
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import account_id
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response, entity_error
# control/company/delete_company_profile_controller.py: controller used to relay this page's entity requests.
from control.company.delete_company_profile_controller import DeleteCompanyProfileController


class DeleteCompanyProfilePage(MethodView):
    def get(self):
        """Retrieve existing details through the View controller and ask for confirmation."""
        accountId = account_id()
        profile = ViewCompanyProfileController().getCompanyProfile(accountId)
        if profile is None:
            return error_response('Company profile not found.', status=404)
        return present(dict(ok=True, confirmationRequired=True, profile=company_values(profile)))

    def post(self):
        """Read the submitted input, call onDelete, and return the prepared response."""
        self.onDelete()
        return self.rendered_page

    def onDelete(self) -> None:
        """Call the imported deletion controller and display success or saved-data errors."""
        accountId = account_id()
        controller = DeleteCompanyProfileController()
        if controller.deleteCompanyProfile(accountId):
            self.displaySuccess()
        else:
            self.rendered_page = entity_error(controller)

    def displaySuccess(self) -> None:
        """Display the successful operation through the imported present helper."""
        self.rendered_page = present(dict(ok=True, message='Company profile deleted successfully.'), 200)
