from flask import request
from flask.views import MethodView
# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, search_text
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
# boundary/designer/context.py: submitted values and signed-in account context.
from boundary.designer.context import account_id, request_values
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import present, error_response
# control/customer/search_shortlist_idp_controller.py: the boundary-to-entity request handler.
from control.customer.search_shortlist_idp_controller import SearchShortlistIDPController
# control/customer/dashboard_controller.py: the boundary-to-entity request handler.
from control.customer.dashboard_controller import CustomerDashboardController
# entity/projects/interior_design_project.py: saved project data.
from entity.projects.interior_design_project import InteriorDesignProject


class SearchShortlistIDPPage(MethodView):
    def get(self):
        """Display the signed-in customer's matching saved projects."""
        self.onSearch(request.args.get('q',''))
        return self.rendered_page

    def post(self):
        """Read the submitted request, run onSearch, and return the prepared response."""
        self.onSearch(request_values().get('keyword', request_values().get('q','')))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        """Validate the keyword, then request matching records through the search controller."""
        try:
            self.keyword = search_text(strip_input(keyword))
        except DomainError as error:
            self.rendered_page = error_response(str(error), 'customer', {'keyword': [str(error)]})
            return
        self.owner = account_id()
        idps = SearchShortlistIDPController().search_shortlist_IDP(self.owner, self.keyword)
        self.displayResults(idps)

    def displayResults(self, idps: list[InteriorDesignProject]) -> None:
        """Display the returned records using the shared portal presenter."""
        saved = CustomerDashboardController().savedProjectIds(self.owner)
        self.rendered_page = present(dict(ok=True, projects=[p.as_public_dict() for p in idps],
            query=self.keyword, savedIds=saved, shortlisted=True),
            'customer/projects.html', 'Search My Shortlist', 'customer')
