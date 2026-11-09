from flask import request
from flask.views import MethodView
from boundary.validation import strip_input
from boundary.designer.context import request_values
from boundary.portal import optional_account_id, present
from control.customer.search_idp_controller import SearchIDPController
from control.customer.dashboard_controller import CustomerDashboardController
from entity.projects.interior_design_project import InteriorDesignProject


class SearchIDPPage(MethodView):
    def get(self):
        self.onSearch(request.args.get('q',''))
        return self.rendered_page

    def post(self):
        self.onSearch(request_values().get('keyword', request_values().get('q','')))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = strip_input(keyword)
        self.owner = optional_account_id()
        idps = SearchIDPController().search_all_IDPs(self.keyword)
        self.displayResults(idps)

    def displayResults(self, idps: list[InteriorDesignProject]) -> None:
        saved = CustomerDashboardController().savedProjectIds(self.owner)
        self.rendered_page = present(dict(ok=True, projects=[p.as_public_dict() for p in idps],
            query=self.keyword, savedIds=saved, shortlisted=False),
            'customer/projects.html', 'Search Interior Design Projects', 'customer')
