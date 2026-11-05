from __future__ import annotations

from typing import TYPE_CHECKING
from flask import render_template
from flask.views import MethodView
from boundary.validation import valid_account_id
from control.accounts.view_user_account_controller import ViewUserAccountController

if TYPE_CHECKING:
    from entity.accounts.user_account import UserAccount


class ViewUserAccountPage(MethodView):

    def get(self, account_id):
        self.onView(account_id)
        return self.rendered_page

    def onView(self, accountId: str) -> None:
        account = (ViewUserAccountController().getUserAccount(accountId)
                   if valid_account_id(accountId) else None)
        if account is None:
            self.rendered_page = render_template(
                'error.html', code=404, message='User account not found.',
                title='User Account Not Found'), 404
        else:
            self.displayAccount(account)

    def displayAccount(self, account: UserAccount) -> None:
        self.rendered_page = render_template(
            'accounts/detail.html', account=account, title='View User Accounts')
