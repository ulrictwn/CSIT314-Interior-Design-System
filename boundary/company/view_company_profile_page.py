from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/company/presentation.py: company form fields and display values.
from boundary.company.presentation import company_values
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import account_id
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/company/view_company_profile_controller.py: controller used to relay this page's entity requests.
from control.company.view_company_profile_controller import ViewCompanyProfileController
# entity/company/company_profile.py: company records and database operations.
from entity.company.company_profile import CompanyProfile


class ViewCompanyProfilePage(MethodView):
    def get(self):
        """Open the selected record through the diagram onView method."""
        self.onView()
        return self.rendered_page

    def onView(self) -> None:
        """Retrieve the selected record through the imported View controller."""
        accountId = account_id()
        profile = ViewCompanyProfileController().getCompanyProfile(accountId)
        if profile is None:
            self.rendered_page = error_response('Company profile not found.', status=404)
        else:
            self.displayCompanyProfile(profile)

    def displayCompanyProfile(self, profile: CompanyProfile) -> None:
        """Prepare the retrieved details for the imported HTML/JSON presenter."""
        self.rendered_page = present(dict(ok=True, profile=company_values(profile)), 200)
