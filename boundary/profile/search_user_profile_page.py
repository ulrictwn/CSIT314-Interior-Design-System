from control.profile.view_user_profile_controller import ViewUserProfileController
from flask import render_template, request, flash
from flask.views import MethodView
# Ordinary input cleanup from boundary/validation.py; entities validate the values.
from boundary.validation import strip_input
# Controller used to relay this boundary request from control/profile/search_user_profile_controller.py.
from control.profile.search_user_profile_controller import SearchUserProfileController
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError

# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class SearchUserProfilePage(MethodView):

    def get(self):
        """Display all profiles initially or submit the entered search.

        Uses control/profile/search_user_profile_controller.py.
        """
        self.keyword = request.args.get('q', '')
        if 'q' in request.args:
            self.onSearch(self.keyword)
        else:
            self.displayResults(ViewUserProfileController().listUserProfiles())
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        """Strip the search text and display matches or the entity's validation error.

        Uses control/profile/search_user_profile_controller.py, boundary/validation.py.
        """
        self.keyword = keyword
        controller = SearchUserProfileController()
        try:
            keyword = strip_input(keyword)
            profiles = controller.searchUserProfiles(keyword)
        except DomainError as error:
            flash(str(error), 'error')
            profiles = ViewUserProfileController().listUserProfiles()
        self.displayResults(profiles)

    def displayResults(self, profiles: list[UserProfile]) -> None:
        """Render the profile search results and entered keyword."""
        self.rendered_page = render_template(
            'profiles/search.html', profiles=profiles, query=self.keyword,
            title='Search User Profiles')
