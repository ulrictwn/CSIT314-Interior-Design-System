# boundary/dashboard_page.py: provides the boundary classes used by these routes.
from boundary.dashboard_page import HomePage, DashboardPage
# boundary/auth/user_admin_login_page.py: provides the boundary classes used by these routes.
from boundary.auth.user_admin_login_page import UserAdminLoginPage
# boundary/auth/logout_page.py: provides the boundary classes used by these routes.
from boundary.auth.logout_page import LogoutPage
# boundary/accounts/account_pages.py: provides the boundary classes used by these routes.
from boundary.accounts.account_pages import UserAccountsPage
# boundary/accounts/create_user_account_page.py: provides the boundary classes used by these routes.
from boundary.accounts.create_user_account_page import CreateUserAccountPage
# boundary/accounts/view_user_account_page.py: provides the boundary classes used by these routes.
from boundary.accounts.view_user_account_page import ViewUserAccountPage
# boundary/accounts/update_user_account_page.py: provides the boundary classes used by these routes.
from boundary.accounts.update_user_account_page import UpdateUserAccountPage
# boundary/accounts/suspend_user_account_page.py: provides the boundary classes used by these routes.
from boundary.accounts.suspend_user_account_page import SuspendUserAccountPage
# boundary/accounts/search_user_account_page.py: provides the boundary classes used by these routes.
from boundary.accounts.search_user_account_page import SearchUserAccountPage
# boundary/profile/create_user_profile_page.py: provides the boundary classes used by these routes.
from boundary.profile.create_user_profile_page import CreateUserProfilePage
# boundary/profile/view_user_profile_page.py: provides the boundary classes used by these routes.
from boundary.profile.view_user_profile_page import ViewUserProfilePage
# boundary/profile/update_user_profile_page.py: provides the boundary classes used by these routes.
from boundary.profile.update_user_profile_page import UpdateUserProfilePage
# boundary/profile/suspend_user_profile_page.py: provides the boundary classes used by these routes.
from boundary.profile.suspend_user_profile_page import SuspendUserProfilePage
# boundary/profile/search_user_profile_page.py: provides the boundary classes used by these routes.
from boundary.profile.search_user_profile_page import SearchUserProfilePage
# boundary/profile/profile_pages.py: provides the boundary classes used by these routes.
from boundary.profile.profile_pages import UserProfilesPage


def register_routes(app):
    """Register admin URLs and load the designer/customer/manager boundary route modules."""
    routes = [
        ('/', 'home', HomePage), ('/dashboard', 'dashboard', DashboardPage),
        ('/login', 'login', UserAdminLoginPage), ('/logout', 'logout', LogoutPage),
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

    # boundary/designer/routes.py: provides the boundary classes used by these routes.
    from boundary.designer.routes import register_designer_routes
    register_designer_routes(app)
    # boundary/sprint_routes.py: provides the boundary classes used by these routes.
    from boundary.sprint_routes import register_sprint_routes
    register_sprint_routes(app)
