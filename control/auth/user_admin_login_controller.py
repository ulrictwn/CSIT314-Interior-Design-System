from entity.accounts.user_account import UserAccount


class UserAdminLoginController:
    def __init__(self):
        self.entity = UserAccount()

    def login(self, username: str, password: str) -> bool:
        return self.entity.login(username, password, 'User Admin')
