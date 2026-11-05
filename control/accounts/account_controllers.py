from control.accounts.create_user_account_controller import CreateUserAccountController
from control.accounts.view_user_account_controller import ViewUserAccountController
from control.accounts.update_user_account_controller import UpdateUserAccountController
from control.accounts.suspend_user_account_controller import SuspendUserAccountController
from control.accounts.search_user_account_controller import SearchUserAccountController
from entity.accounts.user_account import UserAccount


class AccountDirectoryController:
    def listForAction(self):
        return UserAccount.searchUserAccounts()
