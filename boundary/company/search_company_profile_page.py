from flask import request
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.validation import strip_input
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.company.search_company_profile_controller import SearchCompanyProfileController


class SearchCompanyProfilePage(MethodView):
    def get(self):
        self.onSearch(request.args.get('q', request.args.get('keyword', '')))
        return self.rendered_page

    def post(self):
        values = request_values()
        self.onSearch(values.get('keyword', values.get('q', '')))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = keyword
        keyword = strip_input(keyword)
        accountId = account_id()
        results = SearchCompanyProfileController().searchCompanyProfile(accountId, keyword)
        self.displayResults(results)

    def displayResults(self, results: list[str]) -> None:
        self.rendered_page = present(dict(ok=True, query=self.keyword, results=results), 200)
