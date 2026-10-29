from datetime import timedelta
from entity.accounts.user_account import UserAccount
from entity.auth.login_session import LoginSession


class LoginController:
    def __init__(self, *, remote_address='', attempt_limit=5, previous_token=None,
                 session_lifetime=timedelta(minutes=30)):
        self.remote_address = remote_address
        self.attempt_limit = attempt_limit
        self.previous_token = previous_token
        self.session_lifetime = session_lifetime

    def login(self, username: str, password: str) -> bool:
        account = UserAccount()
        authenticated = account.login(username, password, remote_address=self.remote_address,
                                      attempt_limit=self.attempt_limit)
        self.error_message = account.error_message
        self.field_errors = account.field_errors
        self.account = account.authenticated_account
        self.session_data = None
        if authenticated:
            self.session_data = LoginSession.start(self.account, self.session_lifetime,
                                                   previous_token=self.previous_token)
        return authenticated
