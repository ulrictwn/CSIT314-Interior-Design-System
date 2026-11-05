from entity.accounts.user_account import UserAccount


class LoginController:
    def login(self, username: str, password: str) -> bool:
        account = UserAccount()
        authenticated = account.login(username, password)
        self.error_message = account.error_message
        self.account = account.authenticated_account
        return authenticated
