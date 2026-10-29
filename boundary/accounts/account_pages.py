from flask import render_template, request
from boundary.base import Page
from boundary.accounts.create_user_account_page import CreateUserAccountPage
from boundary.accounts.view_user_account_page import ViewUserAccountPage
from boundary.accounts.update_user_account_page import UpdateUserAccountPage
from boundary.accounts.suspend_user_account_page import SuspendUserAccountPage
from boundary.accounts.search_user_account_page import SearchUserAccountPage
from control.accounts.account_controllers import AccountDirectoryController
from infrastructure.errors import AccessError


class UserAccountsPage(Page):
    def get(self):
        mode = request.args.get('mode', 'view')
        if not any(self.actor.has_permission('account.'+action) for action in ('create','view','update','suspend','search')):
            raise AccessError('You do not have permission to access user accounts.')
        accounts = None if mode == 'view' and not self.actor.has_permission('account.view') else AccountDirectoryController(self.actor).listForAction(mode)
        return render_template('accounts/index.html', accounts=accounts, mode=mode, title=mode.title()+' User Accounts')
