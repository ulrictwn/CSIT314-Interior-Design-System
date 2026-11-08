from flask import request
from flask.views import MethodView
from boundary.validation import strip_input
from boundary.designer.context import account_id, request_values
from boundary.portal import present
from control.customer.search_shortlist_idp_controller import SearchShortlistIDPController
from control.customer.dashboard_controller import CustomerDashboardController
from entity.projects.interior_design_project import InteriorDesignProject


class SearchShortlistIDPPage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        self.onSearch(request.args.get('q',''))
        return self.rendered_page

    def post(self):
        self.onSearch(request_values().get('keyword', request_values().get('q','')))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = strip_input(keyword)
        self.owner = account_id(self.accountId)
        idps = SearchShortlistIDPController().search_shortlist_IDP(self.owner, self.keyword)
        self.displayResults(idps)

    def displayResults(self, idps: list[InteriorDesignProject]) -> None:
        saved = CustomerDashboardController().savedProjectIds(self.owner)
        self.rendered_page = present(dict(ok=True, projects=[p.as_public_dict() for p in idps],
            query=self.keyword, savedIds=saved, shortlisted=True),
            'customer/projects.html', 'Search My Shortlist', 'customer')
