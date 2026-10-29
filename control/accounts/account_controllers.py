from control.base import Controller
from control.accounts.create_user_account_controller import CreateUserAccountController
from control.accounts.view_user_account_controller import ViewUserAccountController
from control.accounts.update_user_account_controller import UpdateUserAccountController
from control.accounts.suspend_user_account_controller import SuspendUserAccountController
from control.accounts.search_user_account_controller import SearchUserAccountController
from entity.accounts.user_account import UserAccount
from infrastructure.errors import DomainError


class AccountDirectoryController(Controller):
    def listForAction(self, mode='view'):
        permission = {'view': 'account.view', 'update': 'account.update', 'suspend': 'account.suspend'}.get(mode)
        if permission is None:
            raise DomainError('Choose a supported account operation.')
        self.require(permission)
        return UserAccount.searchUserAccounts()
