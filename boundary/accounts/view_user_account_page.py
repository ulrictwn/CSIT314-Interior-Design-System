from flask import render_template
from flask.views import MethodView
# Ordinary input cleanup from boundary/validation.py; entities validate the values.
from boundary.validation import strip_input
# Controller used to relay this boundary request from control/accounts/view_user_account_controller.py.
from control.accounts.view_user_account_controller import ViewUserAccountController

# Entity used for saved data or return-value types from entity/accounts/user_account.py.
from entity.accounts.user_account import UserAccount


class ViewUserAccountPage(MethodView):

    def get(self, account_id):
        """Pass the selected account ID to the diagram onView event."""
        self.onView(account_id)
        return self.rendered_page

    def onView(self, accountId: str) -> None:
        """Pass the stripped ID to the entity through the view controller.

        Uses boundary/validation.py, control/accounts/view_user_account_controller.py.
        """
        accountId = strip_input(accountId)
        account = ViewUserAccountController().getUserAccount(accountId)
        if account is None:
            self.rendered_page = render_template(
                'error.html', code=404, message='User account not found.',
                title='User Account Not Found'), 404
        else:
            self.displayAccount(account)

    def displayAccount(self, account: UserAccount) -> None:
        """Render the selected account details."""
        self.rendered_page = render_template(
            'accounts/detail.html', account=account, title='View User Accounts')
