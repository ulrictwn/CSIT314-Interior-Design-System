from __future__ import annotations

from typing import TYPE_CHECKING
from flask import render_template, request, flash
from boundary.base import Page
from control.accounts.search_user_account_controller import SearchUserAccountController
from infrastructure.errors import DomainError, AccessError

if TYPE_CHECKING:
    from entity.accounts.user_account import UserAccount


class SearchUserAccountPage(Page):
    permission = 'account.search'

    def get(self):
        self.onSearch(request.args.get('q', ''))
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = keyword
        try:
            accounts = SearchUserAccountController(self.actor).searchUserAccounts(keyword)
        except AccessError:
            raise
        except DomainError as error:
            flash(str(error), 'error')
            accounts = []
        self.displayResults(accounts)

    def displayResults(self, accounts: list[UserAccount]) -> None:
        self.rendered_page = render_template(
            'accounts/search.html', query=self.keyword, accounts=accounts,
            title='Search User Accounts')
