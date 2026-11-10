from flask import render_template, request
from flask.views import MethodView
# Controller used to relay this boundary request from control/accounts/search_user_account_controller.py.
from control.accounts.search_user_account_controller import SearchUserAccountController
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError


class UserAccountsPage(MethodView):
    def get(self):
        """Display accounts with the selected view, update or suspend action.

        Uses control/accounts/search_user_account_controller.py.
        """
        mode = request.args.get('mode', 'view')
        if mode not in ('view', 'update', 'suspend'):
            raise DomainError('Choose a supported account operation.')
        accounts = SearchUserAccountController().searchUserAccounts('')
        return render_template('accounts/index.html', accounts=accounts, mode=mode,
            title=mode.title() + ' User Accounts')
