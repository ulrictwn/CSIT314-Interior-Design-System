from boundary.dashboard_page import HomePage, DashboardPage
from boundary.auth_pages import LoginPage, LogoutPage
from boundary.account_pages import (UserAccountsPage, CreateUserAccountPage, ViewUserAccountPage,
    UpdateUserAccountPage, SuspendUserAccountPage, SearchUserAccountPage)
from boundary.profile_pages import (UserProfilesPage, CreateUserProfilePage, ViewUserProfilePage,
    UpdateUserProfilePage, SuspendUserProfilePage, SearchUserProfilePage)


def register_routes(app):
    routes = [
        ('/', 'home', HomePage), ('/dashboard', 'dashboard', DashboardPage),
        ('/login', 'login', LoginPage), ('/logout', 'logout', LogoutPage),
        ('/accounts', 'user_accounts', UserAccountsPage),
        ('/accounts/create', 'create_user_account', CreateUserAccountPage),
        ('/accounts/search', 'search_user_accounts', SearchUserAccountPage),
        ('/accounts/<string:account_id>', 'view_user_account', ViewUserAccountPage),
        ('/accounts/<string:account_id>/update', 'update_user_account', UpdateUserAccountPage),
        ('/accounts/<string:account_id>/suspend', 'suspend_user_account', SuspendUserAccountPage),
        ('/profiles', 'user_profiles', UserProfilesPage),
        ('/profiles/create', 'create_user_profile', CreateUserProfilePage),
        ('/profiles/search', 'search_user_profiles', SearchUserProfilePage),
        ('/profiles/<int:profile_id>', 'view_user_profile', ViewUserProfilePage),
        ('/profiles/<int:profile_id>/update', 'update_user_profile', UpdateUserProfilePage),
        ('/profiles/<int:profile_id>/suspend', 'suspend_user_profile', SuspendUserProfilePage),
    ]
    for path, name, page in routes:
        app.add_url_rule(path, view_func=page.as_view(name))
