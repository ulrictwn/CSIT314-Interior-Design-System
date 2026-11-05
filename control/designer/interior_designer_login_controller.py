from entity.accounts.user_account import UserAccount


class InteriorDesignerLoginController:
    def login(self, username: str, password: str) -> bool:
        account = UserAccount()
        result = account.login(username, password, 'Interior Designer')
        self.error_message, self.account = account.error_message, account.authenticated_account
        return result
