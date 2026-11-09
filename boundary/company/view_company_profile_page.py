from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.company.presentation import company_values
from boundary.designer.context import account_id
from boundary.designer.responses import error_response
from control.company.view_company_profile_controller import ViewCompanyProfileController
from entity.company.company_profile import CompanyProfile


class ViewCompanyProfilePage(MethodView):
    def get(self):
        self.onView()
        return self.rendered_page

    def onView(self) -> None:
        accountId = account_id()
        profile = ViewCompanyProfileController().getCompanyProfile(accountId)
        if profile is None:
            self.rendered_page = error_response('Company profile not found.', status=404)
        else:
            self.displayCompanyProfile(profile)

    def displayCompanyProfile(self, profile: CompanyProfile) -> None:
        self.rendered_page = present(dict(ok=True, profile=company_values(profile)), 200)
