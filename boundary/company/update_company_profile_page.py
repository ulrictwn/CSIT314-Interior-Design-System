from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.company.validation import COMPANY_FIELDS, validate_company_fields, company_values
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.company.update_company_profile_controller import UpdateCompanyProfileController
from infrastructure.errors import DomainError


class UpdateCompanyProfilePage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        try:
            accountId = account_id(self.accountId)
        except DomainError as error:
            return error_response(str(error), {'accountId': [str(error)]})
        profile = UpdateCompanyProfileController().getCompanyProfile(accountId)
        if profile is None:
            return error_response('Company profile not found.', status=404)
        return present(dict(ok=True, fields=COMPANY_FIELDS, profile=company_values(profile), values=company_values(profile)))

    def post(self):
        values = request_values()
        self.onUpdate(*(values.get(field, '') for field in COMPANY_FIELDS))
        return self.rendered_page

    def onUpdate(self, companyName: str, companyContact: str, companyAddress: str,
                 companyEmail: str, companyRegistrationNumber: str) -> None:
        self.values = dict(zip(COMPANY_FIELDS, [companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber]))
        values, self.field_errors = validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        self.error_reason = 'invalid_data'
        try:
            accountId = account_id(self.accountId)
        except DomainError as error:
            self.field_errors['accountId'] = [str(error)]
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            self.displayError()
            return
        controller = UpdateCompanyProfileController()
        if controller.updateCompanyProfile(accountId, **values):
            self.values = values
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.error_message, controller.field_errors
            self.error_reason = controller.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='Company profile updated successfully.', values=self.values), 200)

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
