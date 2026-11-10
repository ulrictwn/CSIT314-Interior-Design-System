from flask import render_template, request
from flask.views import MethodView
# Controller used to relay this boundary request from control/accounts/search_user_account_controller.py.
from control.accounts.search_user_account_controller import SearchUserAccountController
# Ordinary input cleanup for the directory display option.
from boundary.validation import strip_input


class UserAccountsPage(MethodView):
    def get(self):
        """Display accounts with the selected view, update or suspend action.

        Uses control/accounts/search_user_account_controller.py.
        """
        mode = {'view': 'view', 'update': 'update', 'suspend': 'suspend'}.get(
            strip_input(request.args.get('mode', 'view')), 'view')
        accounts = SearchUserAccountController().searchUserAccounts('')
        return render_template('accounts/index.html', accounts=accounts, mode=mode,
            title=mode.title() + ' User Accounts')
