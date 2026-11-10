from flask import request
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, search_text
# infrastructure/errors.py: application error types.
from infrastructure.errors import DomainError
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import account_id, request_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/company/search_company_profile_controller.py: controller used to relay this page's entity requests.
from control.company.search_company_profile_controller import SearchCompanyProfileController


class SearchCompanyProfilePage(MethodView):
    def get(self):
        """Read the search query and pass it to onSearch."""
        self.onSearch(request.args.get('q', request.args.get('keyword', '')))
        return self.rendered_page

    def post(self):
        """Read the submitted input, call onSearch, and return the prepared response."""
        values = request_values()
        self.onSearch(values.get('keyword', values.get('q', '')))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        """Validate the search text, then request matching records from the imported controller."""
        self.keyword = strip_input(keyword)
        try:
            keyword = search_text(self.keyword)
        except DomainError as error:
            self.rendered_page = error_response(str(error), {'keyword': [str(error)]}, values={'keyword': self.keyword})
            return
        accountId = account_id()
        results = SearchCompanyProfileController().searchCompanyProfile(accountId, keyword)
        self.displayResults(results)

    def displayResults(self, results: list[str]) -> None:
        """Prepare the retrieved details for the imported HTML/JSON presenter."""
        self.rendered_page = present(dict(ok=True, query=self.keyword, results=results), 200)
