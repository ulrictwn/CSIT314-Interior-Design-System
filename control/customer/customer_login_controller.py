from entity.accounts.user_account import UserAccount


class CustomerLoginController:
    def login(self, username: str, password: str) -> bool:
        entity = UserAccount()
        result = entity.login(username, password, 'Customer')
        self.error_message, self.account = entity.error_message, entity.authenticated_account
        return result
