from entity.auth.login_session import LoginSession


class LogoutController:
    def logout(self, token) -> None:
        LoginSession.revoke(token)
