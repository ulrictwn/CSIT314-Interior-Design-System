from flask import request
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.validation import search_text
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.company.search_company_profile_controller import SearchCompanyProfileController
from infrastructure.errors import DomainError


class SearchCompanyProfilePage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        self.onSearch(request.args.get('q', request.args.get('keyword', '')))
        return self.rendered_page

    def post(self):
        values = request_values()
        self.onSearch(values.get('keyword', values.get('q', '')))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = keyword
        try:
            keyword = search_text(keyword)
            accountId = account_id(self.accountId)
        except DomainError as error:
            self.rendered_page = error_response(str(error))
            return
        results = SearchCompanyProfileController().searchCompanyProfile(accountId, keyword)
        self.displayResults(results)

    def displayResults(self, results: list[str]) -> None:
        self.rendered_page = present(dict(ok=True, query=self.keyword, results=results), 200)
