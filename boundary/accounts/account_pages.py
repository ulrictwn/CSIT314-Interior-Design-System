from flask import render_template, request
from flask.views import MethodView
from boundary.accounts.create_user_account_page import CreateUserAccountPage
from boundary.accounts.view_user_account_page import ViewUserAccountPage
from boundary.accounts.update_user_account_page import UpdateUserAccountPage
from boundary.accounts.suspend_user_account_page import SuspendUserAccountPage
from boundary.accounts.search_user_account_page import SearchUserAccountPage
from control.accounts.account_controllers import AccountDirectoryController
from infrastructure.errors import DomainError


class UserAccountsPage(MethodView):
    def get(self):
        mode = request.args.get('mode', 'view')
        if mode not in ('view', 'update', 'suspend'):
            raise DomainError('Choose a supported account operation.')
        accounts = AccountDirectoryController().listForAction()
        return render_template('accounts/index.html', accounts=accounts, mode=mode,
            title=mode.title() + ' User Accounts')
