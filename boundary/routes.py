from boundary.dashboard_page import HomePage, DashboardPage
from boundary.auth.auth_pages import LoginPage, LogoutPage
from boundary.accounts.account_pages import UserAccountsPage
from boundary.accounts.create_user_account_page import CreateUserAccountPage
from boundary.accounts.view_user_account_page import ViewUserAccountPage
from boundary.accounts.update_user_account_page import UpdateUserAccountPage
from boundary.accounts.suspend_user_account_page import SuspendUserAccountPage
from boundary.accounts.search_user_account_page import SearchUserAccountPage
from boundary.profile.create_user_profile_page import CreateUserProfilePage
from boundary.profile.view_user_profile_page import ViewUserProfilePage
from boundary.profile.update_user_profile_page import UpdateUserProfilePage
from boundary.profile.suspend_user_profile_page import SuspendUserProfilePage
from boundary.profile.search_user_profile_page import SearchUserProfilePage
from boundary.profile.profile_pages import UserProfilesPage


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

    from boundary.designer.routes import register_designer_routes
    register_designer_routes(app)
    from boundary.sprint_routes import register_sprint_routes
    register_sprint_routes(app)
