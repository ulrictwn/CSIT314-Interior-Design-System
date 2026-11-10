# control/company/view_company_profile_controller.py: controller used to relay this page's entity requests.
from control.company.view_company_profile_controller import ViewCompanyProfileController
# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/company/presentation.py: company form fields and display values.
from boundary.company.presentation import COMPANY_FIELDS, company_values
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import account_id, request_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/company/update_company_profile_controller.py: controller used to relay this page's entity requests.
from control.company.update_company_profile_controller import UpdateCompanyProfileController


class UpdateCompanyProfilePage(MethodView):
    def get(self):
        """Retrieve existing details through the View controller and prefill the form."""
        accountId = account_id()
        profile = ViewCompanyProfileController().getCompanyProfile(accountId)
        if profile is None:
            return error_response('Company profile not found.', status=404)
        return present(dict(ok=True, fields=COMPANY_FIELDS, profile=company_values(profile), values=company_values(profile)))

    def post(self):
        """Read the submitted input, call onUpdate, and return the prepared response."""
        values = request_values()
        self.onUpdate(*(values.get(field, '') for field in COMPANY_FIELDS))
        return self.rendered_page

    def onUpdate(self, companyName: str, companyContact: str, companyAddress: str,
                 companyEmail: str, companyRegistrationNumber: str) -> None:
        """Strip entered text, then ask the controller/entity to validate and save it."""
        self.values = {field: strip_input(value) for field, value in zip(COMPANY_FIELDS,
            [companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber])}
        controller = UpdateCompanyProfileController()
        if controller.updateCompanyProfile(account_id(), **self.values):
            self.values = company_values(ViewCompanyProfileController().getCompanyProfile(account_id()))
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        """Display the successful operation through the imported present helper."""
        self.rendered_page = present(dict(ok=True, message='Company profile updated successfully.', values=self.values), 200)

    def displayError(self) -> None:
        """Display field or saved-data errors with the submitted values."""
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
