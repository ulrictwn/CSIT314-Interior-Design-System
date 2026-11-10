from flask import render_template, request, flash
from flask.views import MethodView
# Ordinary input cleanup from boundary/validation.py; entities validate the values.
from boundary.validation import strip_input
# Controller used to relay this boundary request from control/accounts/search_user_account_controller.py.
from control.accounts.search_user_account_controller import SearchUserAccountController
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError

# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class SearchUserAccountPage(MethodView):

    def get(self):
        """Submit the entered keyword to the diagram onSearch event."""
        self.onSearch(request.args.get('q', ''))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        """Strip the keyword and request matching accounts; entity validation owns errors.

        Uses boundary/validation.py, control/accounts/search_user_account_controller.py.
        """
        self.keyword = keyword
        try:
            keyword = strip_input(keyword)
            accounts = SearchUserAccountController().searchUserAccounts(keyword)
        except DomainError as error:
            flash(str(error), 'error')
            accounts = []
        self.displayResults(accounts)

    def displayResults(self, accounts: list[UserAccount]) -> None:
        """Render matching accounts and the entered keyword."""
        self.rendered_page = render_template(
            'accounts/search.html', query=self.keyword, accounts=accounts,
            title='Search User Accounts')
