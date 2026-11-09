from flask import render_template, request
from flask.views import MethodView
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
