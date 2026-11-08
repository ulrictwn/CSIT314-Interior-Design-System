from boundary.validation import strip_input
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.company.presentation import COMPANY_FIELDS, company_values
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.company.create_company_profile_controller import CreateCompanyProfileController


class CreateCompanyProfilePage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        return present(dict(ok=True, fields=COMPANY_FIELDS, values={}))

    def post(self):
        values = request_values()
        self.onCreate(*(values.get(field, '') for field in COMPANY_FIELDS))
        return self.rendered_page

    def onCreate(self, companyName: str, companyContact: str, companyAddress: str,
                 companyEmail: str, companyRegistrationNumber: str) -> None:
        self.values = {field: strip_input(value) for field, value in zip(COMPANY_FIELDS,
            [companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber])}
        controller = CreateCompanyProfileController()
        if controller.createCompanyProfile(account_id(), **self.values):
            self.profile = controller.entity
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        self.rendered_page = present(dict(ok=True, message='Company profile created successfully.', profile=company_values(self.profile)), 201)

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, self.field_errors,
            404 if self.error_reason == 'not_found' else 400, self.values)
