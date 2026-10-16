from flask import redirect, url_for
from boundary.profile_pages import (UserProfilesPage, CreateUserProfilePage, ViewUserProfilePage,
    UpdateUserProfilePage, SuspendUserProfilePage, SearchUserProfilePage)


def register_routes(app):
    app.add_url_rule('/', 'home', lambda: redirect(url_for('user_profiles')))
    routes = [
        ('/profiles', 'user_profiles', UserProfilesPage),
        ('/profiles/create', 'create_user_profile', CreateUserProfilePage),
        ('/profiles/search', 'search_user_profiles', SearchUserProfilePage),
        ('/profiles/<int:profile_id>', 'view_user_profile', ViewUserProfilePage),
        ('/profiles/<int:profile_id>/update', 'update_user_profile', UpdateUserProfilePage),
        ('/profiles/<int:profile_id>/suspend', 'suspend_user_profile', SuspendUserProfilePage),
    ]
    for path, name, page in routes:
        app.add_url_rule(path, view_func=page.as_view(name))
