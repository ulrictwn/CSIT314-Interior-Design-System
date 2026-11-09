from entity.accounts.user_account import UserAccount


class AccountDirectoryController:
    def listForAction(self):
        return UserAccount.searchUserAccounts()
